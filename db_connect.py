import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

def db_connect():
	
    load_dotenv()

    user = os.getenv("DB_USER")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_NAME")
    password = os.getenv("DB_PASSWORD")
    port = os.getenv("DB_PORT")
    
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')

    return engine

