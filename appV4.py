import io
import os
import uuid
import json
import requests
from PIL import Image
from ultralytics import YOLO
from datetime import datetime, date
from oss2.exceptions import OssError
from oss_creation import create_bucket
from flask import Flask, request, jsonify, render_template
from db_update import update_rejected_images, update_processed_images
from db_select import select_images, select_products, select_brands, select_name
from img_function import  annotate_image, calculate_area, is_blurred, delete_all_image
from db_insert import insert_rejects, insert_results, insert_result_compliances, insert_oos, insert_sov
from oos_detection import out_of_stock_product, complience_maggi, complience_nestle, nestle_eye_level_check, maggi_eye_level_check

app = Flask(__name__, template_folder='template')

model = YOLO('best.pt')

item_list = [
    "fn kundur",
    "fn lemontea",
    "jnj twin",
    "maggi kari unsorted",
    "maggi kari",
    "maggi tomyam",
    "maggi tomyamunsorted",
    "marigold",
    "mr potato",
    "nestle koko unsorted",
    "nestle koko",
    "nestle milo unsorted",
    "nestle milo",
    "nestle stars unsorted",
    "nestle stars",
    "ping pong",
    "roma malkist",
    "twisties ori",
    "twisties sco",
    "yeos greentea",
    "yeos tebu"
]

@app.route('/')
def index():

    email = request.args.get('email')
    
    return render_template('loader.html',email=email)

@app.route("/api/get_data", methods=["GET"])
def predict():

    email = request.args.get('email')
    time = datetime.now()
    mydate = date.today()
    
    print(f"INFO: {email} initiated API request")

    # Delete original and annotated image folder
    delete_all_image()

    # Create a folder to save the downloaded images
    downloaded_folder = "downloaded_images"
    os.makedirs(downloaded_folder, exist_ok=True)

    # Create a folder to save the downloaded images
    annotated_image_folder = "annotated_images"
    os.makedirs(annotated_image_folder, exist_ok=True)

    # Create an OSS bucket object
    bucket = create_bucket()

    # Use pandas to read the data into a DataFrame
    df = select_images()

    if email is not None:

        myname = select_name(email) 

        length = len(df)
            
        if(length != 0):

            count_processed = 0
            count_rejected = 0

            for index in range(length):
                row = df.loc[index]
                # Access data in each row using row['column_name']
                # Define the string you want to check for
                search_string = 'https://'

                # Use str.contains() to check if the string is present in the 'column_name' column
                urlstring = row['image_path']
                imgid = row['id']
                vuid = row['van_user_id']
                oid = row['outlet_id']

                if search_string in urlstring:
                    # print(urlstring)

                    response = requests.get(urlstring)
                    
                    image_filename = os.path.basename(urlstring)
                    # image_filename = 'temp.jpg'

                    # Use the sanitized filename for file operations
                    sanitized_filename = image_filename.replace(':', '_')

                    image_filename = sanitized_filename
                    
                    image_filename = os.path.join(downloaded_folder, image_filename)

                    if response.status_code == 200:
                        image_data = response.content
                        
                        # download image
                        with open(image_filename, 'wb') as image_file:
                            image_file.write(image_data)
                            # print(f"Image downloaded and saved as {image_filename}",f"image id ={imgid}")
                            
                        with open(image_filename, 'rb') as image_file:
                            image_bytes = image_file.read()
                            img = Image.open(io.BytesIO(image_bytes))

                            # Check and rotate based on EXIF data
                            exif = img._getexif()
                            if exif:
                                orientation = exif.get(0x0112)  # EXIF code for orientation
                                if orientation is not None:
                                    if orientation == 1:
                                        # Normal orientation, no rotation needed
                                        pass
                                    elif orientation == 3:
                                        img = img.rotate(180, expand=True)
                                    elif orientation == 6:
                                        img = img.rotate(270, expand=True)
                                    elif orientation == 8:
                                        img = img.rotate(90, expand=True)
                                                
                            is_image_blurred = is_blurred(image_filename)
                            if(is_image_blurred):

                                rejected_img_id =  uuid.uuid4()
                                rejected_img_reason = "Image blurred"
                                van_user_id = vuid
                                image_id = imgid
                                
                                insert_rejects(rejected_img_id, van_user_id, image_id, rejected_img_reason, time, myname, time, myname, mydate)
                                update_rejected_images(imgid)

                                count_rejected = count_rejected + 1
                                print()
                                print(f"Image {imgid} rejected")

                            else:

                                results = model(img)

                                product_names = [item_list[int(class_label)] for class_label in results[0].boxes.cls.tolist()]
                                # The list is not null (i.e., it contains at least one element)
                                if(len(product_names) >= 10):
                                
                                    areas, labels = calculate_area(results[0].boxes.xyxy.tolist(), results[0].boxes.cls.tolist(), results[0].boxes.conf.tolist(), 0.5)

                                    # Initialize a variable to store the total area
                                    total_area = 0.0

                                    # Initialize a variable to store the maggi_kari_area
                                    maggi_area = 0.0
                                    nestle_area = 0.0

                                    # Print the areas and labels
                                    for area, label in zip(areas, labels):
                                        # print(f"Area of bounding box for {label}: {area:.2f} square pixels")
                                        total_area += area

                                        if "maggi" in label:                
                                            maggi_area += area

                                        if "nestle" in label:                
                                            nestle_area += area

                                    # Annotate the image with bounding boxes and class labels
                                    annotated_img = annotate_image(img, results[0].boxes.xyxy.tolist(), results[0].boxes.cls.tolist(), results[0].boxes.conf.tolist())
                                    
                                    annotated_image_filename = "annotated_" + sanitized_filename
                                    
                                    # Generate a unique filename for the annotated image
                                    annotated_filename = os.path.join(annotated_image_folder, annotated_image_filename)

                                    # Save the annotated image as a JPG file
                                    annotated_img.save(annotated_filename, format="JPEG")
                                            
                                    #start upload image into oss
                                
                                    # Define the desired OSS object key (name) for the image
                                    oss_object_key = "image-annotated/" + annotated_image_filename  # Adjust the key as needed

                                    # Try to upload the image to OSS
                                    try:
                                        bucket.put_object_from_file(oss_object_key, annotated_filename)
                                        # Generate a public access URL for the image
                                        public_access_url = bucket.sign_url('GET', oss_object_key, 315360000)  # 3600 seconds (1 hour) validity

                                        # print(f"Public Access URL for the image: {public_access_url}")
                                        # print(f"Image uploaded successfully to OSS as '{oss_object_key}'")

                                    except OssError as e:
                                        print(f"Failed to upload the image: {e}")

                                    # print(imgid)
                                    if(maggi_area != 0):
                                        sov_maggi = (maggi_area/total_area)*100
                                    else:
                                        sov_maggi = 0
                                        
                                    if(nestle_area != 0):
                                        sov_nestle = (nestle_area/total_area)*100
                                    else:
                                        sov_nestle = 0							

                                    sov_competitor = 100 - (sov_maggi + sov_nestle)
                                    
                                    # Out_of_stock
                                    # Perform out of stock detection
                                    product_names = [item_list[int(class_label)] for class_label in results[0].boxes.cls.tolist()]
                                    oos_maggi_kari,oos_maggi_tomyam, oos_nestle_koko, oos_nestle_milo, oos_nestle_star= out_of_stock_product(product_names)
                                    
                                    comp_maggi = "N/A"
                                    eye_level_status_maggi = "N/A"
                                    comp_nestle = "N/A"
                                    eye_level_status_nestle = "N/A"
                                    
                                    if oos_maggi_kari == "No" or oos_maggi_tomyam == "No" :
                                        if oos_nestle_koko == "No" or oos_nestle_milo == "No" or oos_nestle_star == "No":
                                            # Process only complience_nestle and nestle_eye_level_check
                                            comp_maggi = complience_maggi(product_names)
                                            eye_level_status_maggi = maggi_eye_level_check(product_names, results[0].boxes.xyxy.tolist())
                                            comp_nestle = complience_nestle(product_names)
                                            eye_level_status_nestle = nestle_eye_level_check(product_names, results[0].boxes.xyxy.tolist())
                                        else:
                                            comp_maggi = complience_maggi(product_names)
                                            eye_level_status_maggi = maggi_eye_level_check(product_names, results[0].boxes.xyxy.tolist())
                                            comp_nestle = "-"
                                            eye_level_status_nestle = "-"
                                    else:
                                        
                                        if oos_nestle_koko == "No" or oos_nestle_milo == "No" or oos_nestle_star == "No":  
                                            # Process only complience_nestle and nestle_eye_level_check
                                            comp_maggi = "-"
                                            eye_level_status_maggi = "-"
                                            comp_nestle = complience_nestle(product_names)
                                            eye_level_status_nestle = nestle_eye_level_check(product_names, results[0].boxes.xyxy.tolist())
                                        else:
                                            comp_maggi = "-"
                                            eye_level_status_maggi = "-"
                                            comp_nestle = "-"
                                            eye_level_status_nestle = "-"

                                    # Create a Python dictionary
                                    data = {
                                        "SOV Maggi": sov_maggi,
                                        "SOV Nestle": sov_nestle,
                                        "SOV Competitor": sov_competitor,
                                        "Out of Stock Maggi Kari": oos_maggi_kari,
                                        "Out of Stock Maggi Tomyam": oos_maggi_tomyam,
                                        "Out of Stock Nestle Koko": oos_nestle_koko,
                                        "Out of Stock Nestle Milo": oos_nestle_milo,
                                        "Out of Stock Nestle Star": oos_nestle_star,
                                        "Compliance Maggi": comp_maggi,
                                        "Compliance Nestle": comp_nestle,
                                        "Eye Level Maggi": eye_level_status_maggi,
                                        "Eye Level Nestle": eye_level_status_nestle
                                    }

                                    # Convert the dictionary to a JSON string
                                    json_data = json.dumps(data)
                                    
                                    cut_string = public_access_url.split('?')[0]
                                    
                                    update_processed_images(annotated_image_filename, cut_string, json_data, imgid)

                                    result_id = uuid.uuid4()
                                    van_user_id = vuid
                                    image_id = imgid
                                    outlet_id = oid
                        
                                    insert_results(result_id, van_user_id, image_id, outlet_id, time, myname, time, myname)

                                    # access brands table
                                    df_brand = select_brands()
                                    df_bid = df_brand['id']

                                    if(oos_maggi_kari == "No" or oos_maggi_tomyam == "No"):
                                        # insert result compliances for maggi
                                        result_compliances_id = uuid.uuid4()
                                        insert_result_compliances(result_compliances_id, result_id, df_bid.loc[2], comp_maggi, eye_level_status_maggi, time, myname, time, myname)
                                    
                                    if(oos_nestle_koko == "No" or oos_nestle_milo == "No" or oos_nestle_star == "No"):
                                        # insert result compliances for nestle
                                        result_compliances_id = uuid.uuid4()
                                        insert_result_compliances(result_compliances_id, result_id, df_bid.loc[0], comp_nestle, eye_level_status_nestle, time, myname, time, myname)

                                    # access products table
                                    df_prod = select_products()
                                    df_pid = df_prod['id']

                                    # insert oos for maggi kari
                                    oos_id = uuid.uuid4()
                                    insert_oos(oos_id, result_id, df_pid.loc[4], oos_maggi_kari, time, myname, time, myname)

                                    # insert oos for maggi tomyam
                                    oos_id = uuid.uuid4()
                                    insert_oos(oos_id, result_id, df_pid.loc[1], oos_maggi_tomyam, time, myname, time, myname)

                                    # insert oos for nestle koko
                                    oos_id = uuid.uuid4()
                                    insert_oos(oos_id, result_id, df_pid.loc[0], oos_nestle_koko, time, myname, time, myname)

                                    # insert oos for nestle milo
                                    oos_id = uuid.uuid4()
                                    insert_oos(oos_id, result_id, df_pid.loc[3], oos_nestle_milo, time, myname, time, myname)

                                    # insert oos for nestle stars
                                    oos_id = uuid.uuid4()
                                    insert_oos(oos_id, result_id, df_pid.loc[2], oos_nestle_star, time, myname, time, myname)
                                     
                                    # insert result sov for maggi
                                    sov_id = uuid.uuid4()
                                    insert_sov(sov_id, result_id, df_bid.loc[1], round(sov_maggi), time, myname, time, myname)

                                    # insert result sov for nestle
                                    sov_id = uuid.uuid4()
                                    insert_sov(sov_id, result_id, df_bid.loc[0], round(sov_nestle), time, myname, time, myname)

                                    # insert result sov for competitors
                                    sov_id = uuid.uuid4()
                                    insert_sov(sov_id, result_id, df_bid.loc[2], round(sov_competitor), time, myname, time, myname)
                                    
                                    count_processed = count_processed + 1
                                    print(f"Image {imgid} success")
                                    # end process
                                    
                                else:
                                    # The list is null (i.e., it's empty)
                                    rejected_img_id =  uuid.uuid4()

                                    insert_rejects(rejected_img_id, vuid, imgid, "Not related", time, myname, time, myname, mydate)
                                    update_rejected_images(imgid)

                                    count_rejected = count_rejected + 1
                                    print(f"Image {imgid} rejected")

                    else:
                        print(f"Failed to fetch image.")    
                                        
    else:
        print("Email can't be read")
    
    print("INFO: Image processing completed ")
    print(f"INFO: {count_processed} images successfully process")
    print(f"INFO: {count_rejected} images rejected")

    result = {
        'count_rejected': count_rejected,
        'count_processed': count_processed,
        'email': email
    }    
	# return value for flask app
    return jsonify(result)

app.run(host="0.0.0.0", port=8888)