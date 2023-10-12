from flask import Flask, jsonify, abort, request
from PIL import Image, ImageDraw
from roboflow import Roboflow
import os
import cv2
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Access the API key using os.getenv
api_key = os.getenv("API_KEY")

# Initialize a list to store the image data and predictions
image_data_list = []

# Roboflow API endpoint URL
rf = Roboflow(api_key=api_key)
project = rf.workspace().project("planogram-7rx21")
model = project.version(1).model

# Initialize a list to store the image data and predictions
image_data_list = []

app = Flask(__name__)

@app.route("/detect", methods=["POST"])

def process_image():
    file = request.files['image']

    # Save the uploaded image to a temporary file
    temp_file_path = "temp_image.png"  # You can choose a temporary file path
    file.save(temp_file_path)

    # Read the saved image and convert it to RGB mode
    img = Image.open(temp_file_path)

    if img.mode != "RGB":
        img = img.convert("RGB")

    # Save the image as a JPG file
    temp_jpg_path = "temp_image.jpg"
    img.save(temp_jpg_path, "JPEG")

    # Now you can use the saved image path in your model.predict function
    predictions_json = model.predict(temp_jpg_path, confidence=50).json()
    predictions = predictions_json["predictions"]

    total_area = 0

    for prediction in predictions:
        width = prediction["width"]
        height = prediction["height"]
        area = width * height
        total_area += area

    # Class index to calculate total area for (e.g., class_id 0 for 'kelloggs')
    class_index_to_calculate = 0

    # Function to calculate the area of a single object
    def calculate_object_area(object):
        return object["width"] * object["height"]

    # Filter objects by class index
    objects_of_class = [object for object in predictions if object["class_id"] == class_index_to_calculate]

    # Calculate the total area of objects of the specified class
    total_area_0 = sum(calculate_object_area(object) for object in objects_of_class)

    # Percentage of area
    perc = (total_area_0 / total_area) * 100

    # Clean up the temporary file
    os.remove(temp_file_path)

    return jsonify({"msg": "percentage:" + str(int(perc))})


@app.route("/detect-many", methods=["POST"])

def process_many_image():
    files = request.files.to_dict(flat=False) ## files is a list containing two images.


    # Directory containing your images
    input_folder = "uploads"

    # Check if the folder exists, and if not, create it
    if not os.path.exists(input_folder):
        os.makedirs(input_folder)
        
    for i, file_list in enumerate(files.values()):
        for file in file_list:
            # Get the original filename
            original_filename = file.filename

            # Save the file with its original name
            file.save(f'uploads/{original_filename}')

    # List to store image file paths
    image_paths = []

    # Iterate through files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            # If the file is already in JPG format, copy it to the output folder
            image = cv2.imread(os.path.join(input_folder, filename))
            image_paths.append(os.path.join(input_folder, filename))
        else:
            # If the file is not in JPG format, convert it to JPG
            image = cv2.imread(os.path.join(input_folder, filename))
            jpg_filename = os.path.splitext(filename)[0] + ".jpg"
            cv2.imwrite(os.path.join(input_folder, jpg_filename), image)
            image_paths.append(os.path.join(input_folder, jpg_filename))
            # Remove the original non-JPG file
            os.remove(os.path.join(input_folder, filename))

    # Iterate through the list of images and make predictions
    output_folder = "outputs/"

    # Check if the folder exists, and if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    i=0
    for image_path in image_paths:
        with open(image_path, 'rb') as image_file:

            predictions_json = model.predict(image_path, confidence=50).json()
            predictions = predictions_json["predictions"]

            total_area = 0

            # Load the image you want to annotate (replace with your image)
            image = Image.open(image_path)

            for prediction in predictions:
                width = prediction["width"]
                height = prediction["height"]
                area = width * height
                total_area += area

            # Class index to calculate total area for (e.g., class_id 0 for 'kelloggs')
            class_index_to_calculate = 0

            # Function to calculate the area of a single object
            def calculate_object_area(object):
                return object["width"] * object["height"]

            # Filter objects by class index
            objects_of_class = [object for object in predictions if object["class_id"] == class_index_to_calculate]

            # Calculate the total area of objects of the specified class
            total_area_0 = sum(calculate_object_area(object) for object in objects_of_class)

            # Percentage of area
            perc = (total_area_0 / total_area) * 100

            # Load the image you want to annotate (replace with your image)
            image = Image.open(image_path)

            # Create a drawing context
            draw = ImageDraw.Draw(image)

            # Define a dictionary to map class names to different colors
            class_colors = {
                "nestle": "red",
                "kelloggs": "green",
            }

            # Get the base filename (without the extension)
            base_filename, extension = os.path.splitext(os.path.basename(image_path))

            # Create the annotated image filename
            annotated_image_filename = f"{base_filename}_annotated.jpg"

            # Iterate through the predictions and draw bounding boxes
            for prediction in predictions_json["predictions"]:
                x = prediction["x"]
                y = prediction["y"]
                width = prediction["width"]
                height = prediction["height"]
                class_name = prediction["class"]
                
                # Calculate bounding box coordinates
                x1 = x - width / 2
                y1 = y - height / 2
                x2 = x + width / 2
                y2 = y + height / 2

                # Get the color for the class
                box_color = class_colors.get(class_name, "blue")  # Default to blue if class not found

                # Calculate the center of the bounding box
                text_x = (x1 + x2) / 2
                text_y = (y1 + y2) / 2

                # Draw the bounding box with class name and color
                draw.rectangle([x1, y1, x2, y2], outline=box_color, width=5)
                draw.text((text_x, text_y), class_name, fill=box_color)

                # Save the annotated image with the original name + "_annotated"
                annotated_image_path = os.path.join(output_folder, annotated_image_filename)
                image.save(annotated_image_path)

            # Create a dictionary with image data
            image_data = {
                "image_path": annotated_image_filename,
                "total_detected_area": total_area,
                "total_area_of_class_0": total_area_0,
                "total_percentage": format(perc, '.2f')
            }

            image_data_list.append(image_data)

    return jsonify(image_data_list)

if __name__ == "__main__":
    app.run(debug=True)
    