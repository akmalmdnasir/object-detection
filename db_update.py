from sqlalchemy import text
from db_connect import db_connect

# initializa connection engine
engine = db_connect()

def update_rejected_images(imgid):
 
    query = text("UPDATE images SET process_status = :process_status WHERE id = :id")

    # Define the values you want to insert
    values = {"process_status": "Rejected", "id": imgid}

    # Execute the INSERT query
    with engine.begin() as connection:
        connection.execute(query, values)

def update_processed_images(name_string,cut_string,json_data,imgid):

    query = text("UPDATE images SET process_status = :process_status, annotated_name = :annotated_name, annotated_path = :annotated_path, annotated_json = :annotated_json WHERE id = :id")

    # Define the values you want to insert
    values = {"process_status": "Yes", "annotated_name": name_string, "annotated_path": cut_string, "annotated_json": json_data, "id": imgid}
    # Execute the INSERT query
    with engine.begin() as connection:
        connection.execute(query, values)
