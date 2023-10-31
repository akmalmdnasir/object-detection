import io
from PIL import Image, ImageDraw, ImageFont
import os
from flask import Flask, request, send_file
import nest_asyncio
from pyngrok import ngrok
from ultralytics import YOLO

app = Flask(__name__)
model = YOLO('best_246.pt')

# Specify the folder where you want to save annotated images
output_folder = "annotated_images"

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

@app.route("/objectdetection/", methods=["POST"])
def predict():
    if not request.method == "POST":
        return

    if request.files.get("image"):
        image_file = request.files["image"]
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
        '''

        # Annotate the image with bounding boxes and class labels
        annotated_img = annotate_image(img, results[0].boxes.xyxy.tolist(), results[0].boxes.cls.tolist(), results[0].boxes.conf.tolist())

        # Generate a unique filename for the annotated image
        output_filename = os.path.join(output_folder, "annotated_image.jpg")

        # Save the annotated image as a JPG file
        annotated_img.save(output_filename, format="JPEG")

        # print(f"Annotated image saved at: {output_filename}")
        
        # Return the path to the saved annotated image
        return {"nestle area": f"{((nestle_area/total_area)*100):.2f} %",
                "maggi area": f"{((maggi_area/total_area)*100):.2f} %"            
                }

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
