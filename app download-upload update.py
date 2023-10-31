from flask import Flask, jsonify, abort, request
from PIL import Image, ImageDraw
from roboflow import Roboflow
import os
import cv2
from dotenv import load_dotenv
import oss2
from oss2.exceptions import OssError
import psycopg2
import requests
import pandas as pd
from sqlalchemy import create_engine, text
import json
import numpy as np

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

# Access the API key using os.getenv
api_key = os.getenv("API_KEY")

# Initialize a list to store the image data and predictions
image_data_list = []

# Database connection settings
user = 'rnd_user'
host = '47.250.10.195'
database = 'amast_rnd'
password = 'rnduser%40123'
port = 5432

db_config = {
            
    'dbname': database,
    'user': user,
    'password': password,
    'host': host,
    'port': port
}

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

# Create a folder to save the downloaded images
output_folder = "downloaded_images"
os.makedirs(output_folder, exist_ok=True)

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
        image_filename = os.path.join(output_folder, image_filename)


        if response.status_code == 200:
            image_data = response.content
            
            # download image
            with open(image_filename, 'wb') as image_file:
                image_file.write(image_data)
                print(f"Image downloaded and saved as {image_filename}",f"image id ={imgid}")

                image_data_list.append(image_data)

                #start upload image into oss
            
                # Define the desired OSS object key (name) for the image
                oss_object_key = f'image-annotated/{sanitized_filename}'  # Adjust the key as needed

                # Try to upload the image to OSS
                try:
                    bucket.put_object_from_file(oss_object_key, image_filename)
                    # Generate a public access URL for the image
                    public_access_url = bucket.sign_url('GET', oss_object_key, 315360000)  # 3600 seconds (1 hour) validity

                    print(f"Public Access URL for the image: {public_access_url}")
                    print(f"Image uploaded successfully to OSS as '{oss_object_key}'")

                except OssError as e:
                    print(f"Failed to upload the image: {e}")

                #start update url into db
                update_query = text("UPDATE table_oss SET output_path = :output_path WHERE id = :id")

                print(imgid)
                
                # Create an example NumPy int64
                numpy_int64_value = np.int64(imgid)
                

                # Convert the NumPy int64 to a standard Python int
                python_int_value = int(numpy_int64_value)
                imgid = python_int_value


                # Define the parameters for the update query
                update_params = {
                    'output_path': public_access_url,  # Replace with the new output path
                    'id': imgid  # Replace with the specific ID you want to update
                }

                update_query = text("UPDATE table_oss SET output_path = :output_path WHERE id = :id")

                with engine.begin() as connection:
                    connection.execute(update_query, {"output_path": public_access_url, "id": imgid})

                # end process

        else:
            print(f"Failed to fetch image.")

# delete image
# os.remove(image_filename)
# print(f"File {image_filename} has been deleted.")
# os.remove(annotated_image_filename)
# print(f"File {annotated_image_filename} has been deleted.")
# print(json.dumps(image_data_list, indent=4))

# Close the database connection
conn.close()

import shutil

folder_to_delete = "downloaded_images"

# Use shutil.rmtree to delete the folder and its contents
shutil.rmtree(folder_to_delete)