import os
import glob
from PIL import Image
from ultralytics import YOLO
from img_function import  annotate_image

model = YOLO('best_246.pt')

item_list = [
"fn kundur",
"fn lemontea",
"jnj twin",
"maggi kari",
"maggi kari unsorted",
"maggi tomyam",
"maggi tomyamunsorted",
"marigold",
"mr potato",
"nestle koko",
"nestle koko unsorted",
"nestle milo",
"nestle milo unsorted",
"nestle stars",
"nestle stars unsorted",
"ping pong",
"roma malkist",
"twisties ori",
"twisties sco",
"yeos greentea",
"yeos tebu"
]

# Create a folder to save the downloaded images
output_folder = "output_images"
os.makedirs(output_folder, exist_ok=True)

path = 'C:/Users/AKMAL MD NASIR/Downloads/dataset-20231019T061224Z-001/dataset/'

i = 1
for image_path in glob.glob(f'{path}/*.jpg')[:5]:
    with Image.open(image_path) as img:
        # Check and rotate based on EXIF data
        print(f"Processing image {i}")
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

        product_names = [item_list[int(class_label)] for class_label in results[0].boxes.cls.tolist()]

        # Annotate the image with bounding boxes and class labels
        annotated_img = annotate_image(img, results[0].boxes.xyxy.tolist(), results[0].boxes.cls.tolist(), results[0].boxes.conf.tolist())

        filename = os.path.basename(image_path)

        annotated_image_filename = "annotated_" + filename

        # Generate a unique filename for the annotated image
        annotated_filename = os.path.join(output_folder, annotated_image_filename)

        # Save the annotated image as a JPG file
        annotated_img.save(annotated_filename, format="JPEG")
    i = i + 1