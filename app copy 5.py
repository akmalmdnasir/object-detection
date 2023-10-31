import io
from PIL import Image, ImageDraw, ImageFont
import os
from flask import Flask, request, send_file
import nest_asyncio
from pyngrok import ngrok
from ultralytics import YOLO
from flask import Flask, jsonify, abort, request
from dotenv import load_dotenv
import oss2
from oss2.exceptions import OssError
import requests
import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np

app = Flask(__name__)
model = YOLO('best_246.pt')

# Create a folder to save the downloaded images
downloaded_folder = "downloaded_images"
os.makedirs(downloaded_folder, exist_ok=True)

# Create a folder to save the downloaded images
annotated_image_folder = "annotated_image_folder"
os.makedirs(annotated_image_folder, exist_ok=True)

@app.route("/objectdetection/", methods=["GET"])
def predict():

	# Load environment variables from the .env file
	load_dotenv()

	# Access the API key using os.getenv
	# Define your access key ID and access key secret
	access_key_id = os.getenv("ACCESS_KEY_ID")
	access_key_secret = os.getenv("ACCESS_KEY_SECRET")

	# Define the OSS endpoint and bucket name
	endpoint = os.getenv("OSS_ENDPOINT")
	bucket_name = os.getenv("BUCKET_NAME")

	# Create an OSS auth instance
	auth = oss2.Auth(access_key_id, access_key_secret)

	# Create an OSS bucket object
	bucket = oss2.Bucket(auth, endpoint, bucket_name)

	# Database connection settings
	user = 'rnd_user'
	host = '47.250.10.195'
	database = 'amast_rnd'
	password = 'rnduser%40123'
	port = 5432

	# Database connection settings
	# Create a SQLAlchemy engine
	engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

	# Replace 'your_table' with your actual table name
	table_name = 'table_oss'

	# Connect to the database
	conn = engine.connect()

	# Query to fetch data from the table
	query = text(f"SELECT * FROM {table_name}")

	# Use pandas to read the data into a DataFrame
	df = pd.read_sql(query, con=conn)

	# print(df.head(5))

	# Now, 'df' contains the data from the database table in a DataFrame
	# print(df['image_path'])
	length = len(df)
	# length = 3

	for index in range(length):
		row = df.loc[index]
		# Access data in each row using row['column_name']
		# Define the string you want to check for
		search_string = 'https://'

		# Use str.contains() to check if the string is present in the 'column_name' column
		urlstring = row['image_path']
		imgid = row['id']

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
					print(f"Image downloaded and saved as {image_filename}",f"image id ={imgid}")
					
				with open(image_filename, 'rb') as image_file:
					image_bytes = image_file.read()
					img = Image.open(io.BytesIO(image_bytes))

					# rotate image
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

					results = model(img)

					# print(results)
					
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

					'''
					print(f"Total area of all bounding box: {total_area:.2f} square pixels")
					print(f"Total area of maggi bounding box: {maggi_area:.2f} square pixels")
					print(f"Percentage of maggi area: {((maggi_area/total_area)*100):.2f} %")
					print(f"Total area of nestle bounding box: {nestle_area:.2f} square pixels")
					print(f"Percentage of nestle area: {((nestle_area/total_area)*100):.2f} %")

					percentage_sov = ((nestle_area/total_area)*100) + ((maggi_area/total_area)*100)

					'''


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

						print(f"Public Access URL for the image: {public_access_url}")
						print(f"Image uploaded successfully to OSS as '{oss_object_key}'")

					except OssError as e:
						print(f"Failed to upload the image: {e}")

					print(imgid)
					
					# Create an example NumPy int64
					numpy_int64_value = np.int64(imgid)
					
					# Convert the NumPy int64 to a standard Python int
					python_int_value = int(numpy_int64_value)
					imgid = python_int_value

					import json

					# Calculate percentage
					sov_maggi =  (maggi_area/total_area)*100
					sov_nestle = (nestle_area/total_area)*100
					sov_competitor = 100 - (((nestle_area/total_area)*100) + ((maggi_area/total_area)*100))

					# Create a Python dictionary
					data = {
						"sov_maggi": sov_maggi,
						"sov_nestle": sov_nestle,
						"sov_competitor": sov_competitor,
					}

					# Convert the dictionary to a JSON string
					json_data = json.dumps(data)
					
					#start update url into db
					update_query = text("UPDATE table_oss SET output_path = :output_path, json_data = :json_data WHERE id = :id")

					with engine.begin() as connection:
						connection.execute(update_query, {"output_path": public_access_url, "json_data": json_data, "id": imgid})

					# end process

			else:
				print(f"Failed to fetch image.")

			
	# Close the database connection
	conn.close()
	return None
	

def load_class_labels_colors(filename):
    class_labels = {}
    with open(filename, 'r') as file:
        for line in file:
            label, color = line.strip().split(': ')
            r, g, b = map(int, color.split(', '))
            class_labels[label] = (r, g, b)
    return class_labels

def annotate_image(image, boxes, classes, confidence_scores):
    # Create a copy of the input image
    img_draw = image.copy()
    draw = ImageDraw.Draw(img_draw)
    font = ImageFont.truetype("arial.ttf", 20)

    # Load class labels and associated colors from a file
    class_labels = load_class_labels_colors('class_labels.txt')

    for box, class_label, confidence_scores in zip(boxes, classes, confidence_scores):
        x_min, y_min, x_max, y_max = box
        class_label = int(class_label)

        if confidence_scores > 0.5:
            # Get the label name based on class_label
            label_name = list(class_labels.keys())[class_label]
            class_label_text = f"Class: {label_name}"

            # Draw a bounding box around the detected object
            draw.rectangle([x_min, y_min, x_max, y_max], outline=class_labels[label_name], width=2)

            # Display the class label and confidence score on the image
            text_to_display = f"{class_label_text} - Confidence: {confidence_scores:.2f}"
            draw.text((x_min, y_min), text_to_display, fill=class_labels[label_name], font=font)

    # Return the annotated image
    return img_draw

def load_class_labels(filename):
    with open(filename, 'r') as file:
        class_labels = file.read().splitlines()
    return class_labels

def calculate_area(boxes, classes, confidence_scores, threshold):
    # Initialize lists to store areas and labels
    areas = []
    labels = []

    # Load class labels from a text file
    class_labels = load_class_labels("class_labels.txt")

    # Loop through the boxes, classes, and confidence scores
    for box, class_label, confidence_score in zip(boxes, classes, confidence_scores):
        # Check if the confidence score is above the threshold
        if confidence_score > threshold:
            x_min, y_min, x_max, y_max = box
            # Calculate the width and height of the bounding box
            width = x_max - x_min
            height = y_max - y_min
            # Calculate the area of the bounding box
            area = width * height
            # Convert the class label to an integer
            class_label = int(class_label)
            # Get the label name from the class_labels list
            label_name = class_labels[class_label]

            # Append the area and label to their respective lists
            areas.append(area)
            labels.append(label_name)

    # Return the lists of areas and labels
    return areas, labels

ngrok_tunnel = ngrok.connect(8000)
print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
app.run(host="0.0.0.0", port=8000)
