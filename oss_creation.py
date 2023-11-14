import os
import oss2
from dotenv import load_dotenv

def create_bucket():
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
	
	return bucket