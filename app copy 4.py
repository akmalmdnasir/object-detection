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
        results = model(img)

        # Annotate the image with bounding boxes and class labels
        annotated_img = annotate_image(img, results[0].boxes.xyxy.tolist(), results[0].boxes.cls.tolist())

        # Generate a unique filename for the annotated image
        output_filename = os.path.join(output_folder, "annotated_image.jpg")

        # Save the annotated image as a JPG file
        annotated_img.save(output_filename, format="JPEG")
        
        # Return the path to the saved annotated image
        return {"result": f"Annotated image saved at: {output_filename}"}

def annotate_image(image, boxes, classes):
    img_draw = image.copy()
    draw = ImageDraw.Draw(img_draw)
    font = ImageFont.truetype("arial.ttf", 20)

    for box, class_label in zip(boxes, classes):
        x_min, y_min, x_max, y_max = box
        class_label = int(class_label)

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
        
        label_name = item_list[class_label]
        class_label_text = f"Class: {label_name}"

        random_colors = [
            (152, 245, 255),
            (253, 40, 143),
            (19, 119, 14),
            (238, 197, 152),
            (58, 172, 216),
            (110, 128, 180),
            (84, 37, 209),
            (159, 223, 131),
            (119, 61, 207),
            (195, 123, 132),
            (20, 196, 56),
            (195, 29, 59),
            (42, 112, 127),
            (225, 90, 9),
            (155, 76, 68),
            (55, 144, 139),
            (207, 95, 5),
            (189, 11, 91),
            (101, 66, 242),
            (171, 232, 84),
            (119, 217, 59)
        ]


        draw.rectangle([x_min, y_min, x_max, y_max], outline=random_colors[class_label], width=2)

        
        draw.text((x_min, y_min), class_label_text, fill=random_colors[class_label], font=font)

    return img_draw

ngrok_tunnel = ngrok.connect(8000)
print('Public URL:', ngrok_tunnel.public_url)
nest_asyncio.apply()
app.run(host="0.0.0.0", port=8000)
