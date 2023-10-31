import io
from PIL import Image, ImageDraw, ImageFont
import os
from flask import Flask, request, send_file, jsonify, render_template, url_for, redirect
import nest_asyncio
from pyngrok import ngrok
from ultralytics import YOLO
from flask_bootstrap import Bootstrap

app = Flask(__name__, template_folder='Template')
Bootstrap(app)

model = YOLO('best_246.pt')

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            image_path = os.path.join('static', uploaded_file.filename)
            uploaded_file.save(image_path)

            with open(image_path, 'rb') as image_file:
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

                # Annotate the image with bounding boxes and class labels
                annotated_img = annotate_image(img, results[0].boxes.xyxy.tolist(), results[0].boxes.cls.tolist(), results[0].boxes.conf.tolist())

                annotated_image_filename = "annotated_" + os.path.basename(image_path)
					
				# Generate a unique filename for the annotated image
                annotated_filename = os.path.join('static', annotated_image_filename)

                # Save the annotated image as a JPG file
                annotated_img.save(annotated_filename, format="JPEG")        

            result = {
                'image_path': annotated_filename,
            }
            return render_template('result.html', result = result)
    return render_template('index.html')

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

ngrok_tunnel = ngrok.connect(8000)
print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
app.run(host="0.0.0.0", port=8000)
