import cv2
from PIL import ImageDraw, ImageFont
import shutil


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
    font = ImageFont.truetype("arial.ttf", 18)

    # Load class labels and associated colors from a file
    class_labels = load_class_labels_colors('class_labels.txt')

    for box, class_label, confidence_scores in zip(boxes, classes, confidence_scores):
        x_min, y_min, x_max, y_max = box
        class_label = int(class_label)

        if confidence_scores > 0.5:
            # Get the label name based on class_label
            label_name = list(class_labels.keys())[class_label]
            #class_label_text = f"Class: {label_name}"

            # Draw a bounding box around the detected object
            draw.rectangle([x_min, y_min, x_max, y_max], outline=class_labels[label_name], width=4)

            score = round(confidence_scores,2)*100

            # Display the class label and confidence score on the image
            text_to_display = f" {round(score)}% {label_name}"

            # Draw the text shadow
            shadow_offset = 1
            shadow_position = (x_min + shadow_offset, y_min + shadow_offset)
            draw.text(shadow_position, text_to_display, fill='white', font=font)

            # Draw the actual text
            text_position = (x_min, y_min)
            draw.text(text_position, text_to_display, fill=class_labels[label_name], font=font)            

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

def is_blurred(image_path, threshold=100):
    image = cv2.imread(image_path)
    if image is None:
        return False  # Not an image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    return blur < threshold

def delete_all_image():
	# Delete original and annotated image folder
	folders_to_delete = [
		"annotated_images",
		"downloaded_images",
	]

	for folder_path in folders_to_delete:
		try:
			shutil.rmtree(folder_path)
			print(f"Folder at {folder_path} has been deleted.")
		except Exception as e:
			print(f"Error deleting folder {folder_path}: {str(e)}")