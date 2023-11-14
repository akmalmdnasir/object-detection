from sqlalchemy import text
from db_connect import db_connect

# initializa connection engine
engine = db_connect()

def insert_results(result_id, van_user_id, image_id, outlet_id, created_at, created_by):
 
    insert_query = text("INSERT INTO results (id, van_user_id, image_id, outlet_id, created_at, created_by) VALUES (:id, :van_user_id, :image_id, :outlet_id, :created_at, :created_by)")

    # Define the values you want to insert
    insert_values = {"id": result_id, "van_user_id": van_user_id, "image_id": image_id, "outlet_id": outlet_id, "created_at": created_at, "created_by": created_by}

    # Execute the INSERT query
    with engine.begin() as connection:
        connection.execute(insert_query, insert_values)


def insert_result_compliances(result_compliances_id, result_id, brand_id, check_position, check_eye_level):
 
    insert_query = text("INSERT INTO result_compliances (id, result_id, brand_id, check_position, check_eye_level) VALUES (:id, :result_id, :brand_id, :check_position, :check_eye_level)")

    # Define the values you want to insert
    insert_values = {"id": result_compliances_id, "result_id": result_id, "brand_id": brand_id, "check_position": check_position, "check_eye_level": check_eye_level}

    # Execute the INSERT query
    with engine.begin() as connection:
        connection.execute(insert_query, insert_values)


def insert_oos(oos_id, result_id, product_id, check_out_of_stock):
 
    insert_query = text("INSERT INTO result_out_of_stocks (id, result_id, product_id, check_out_of_stock) VALUES (:id, :result_id, :product_id, :check_out_of_stock_id)")

    # Define the values you want to insert
    insert_values = {"id": oos_id, "result_id": result_id, "product_id": product_id, "check_out_of_stock_id": check_out_of_stock}

    # Execute the INSERT query
    with engine.begin() as connection:
        connection.execute(insert_query, insert_values)


def insert_sov(sov_id, result_id, brand_id, percentage):
 
    insert_query = text("INSERT INTO result_share_of_voices (id, result_id, brand_id, percentage) VALUES (:id, :result_id, :brand_id, :percentage)")

    # Define the values you want to insert
    insert_values = {"id": sov_id, "result_id": result_id, "brand_id": brand_id, "percentage": percentage}

    # Execute the INSERT query
    with engine.begin() as connection:
        connection.execute(insert_query, insert_values)


def insert_rejects(rejected_img_id,van_user_id,image_id,rejected_img_reason):

    # Define the INSERT query
    insert_query = text("INSERT INTO rejects (id, van_user_id, image_id, reason) VALUES (:id, :van_user_id, :image_id, :reason)")

    # Define the values you want to insert
    insert_values = {"id": rejected_img_id, "van_user_id": van_user_id, "image_id": image_id, "reason": rejected_img_reason}

    # Execute the INSERT query
    with engine.begin() as connection:
        connection.execute(insert_query, insert_values)
    

