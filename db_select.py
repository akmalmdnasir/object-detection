from sqlalchemy import text
from db_connect import db_connect
import pandas as pd

# initializa connection engine
engine = db_connect()

def select_images():
	
	# Connect to the database
	conn = engine.connect()

	# Query to fetch data from the table
	query = text(f"SELECT * FROM images")

	# Use pandas to read the data into a DataFrame
	df = pd.read_sql(query, con=conn)
	
    # Close the database connection
	conn.close()
	
	return df

def select_products():
	
	# Connect to the database
	conn = engine.connect()

	# Query to fetch data from the table
	query = text(f"SELECT * FROM products")

	# Use pandas to read the data into a DataFrame
	df = pd.read_sql(query, con=conn)
	
    # Close the database connection
	conn.close()
	
	return df

def select_brands():
	
	# Connect to the database
	conn = engine.connect()

	# Query to fetch data from the table
	query = text(f"SELECT * FROM brands")

	# Use pandas to read the data into a DataFrame
	df = pd.read_sql(query, con=conn)
	
    # Close the database connection
	conn.close()
	
	return df

def select_name(filter_condition):
	
	# Connect to the database
	conn = engine.connect()

	# Query to fetch data from the table
	query = text(f"SELECT first_name || ' ' || last_name AS full_name FROM public.admins WHERE email='{filter_condition}'")

	# Use pandas to read the data into a DataFrame
	df = pd.read_sql(query, con=conn)

	df = df['full_name']

	name = df.loc[0]
		
	# Close the database connection
	conn.close()
	
	return name

