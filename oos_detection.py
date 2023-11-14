#out stock of product
def out_of_stock_product(detected_products):
    # List of products to check for out-of-stock
    maggi_kari_to_check = [
        "maggi kari unsorted", "maggi kari"
    ]
    maggi_tomyam_to_check = [
         "maggi tomyam", "maggi tomyamunsorted"
    ]
    nestle_koko_to_check = [
        "nestle koko unsorted", "nestle koko"
    ]
    
    nestle_milo_to_check = [
        "nestle milo unsorted", "nestle milo"
    ]
    nestle_star_to_check = [
        "nestle stars unsorted", "nestle stars"
    ]
    
    
    
    #SOV - Maggi Kari
    # Initialize the out_of_stock status as False
    out_of_stock_kari = True #Out of Stock

    # Check if any of the products are missing in the detected products
    for product in maggi_kari_to_check:
        if product in detected_products: #checkProduct ade dlm list
            # Set out_of_stock to False, bkn OOS
            out_of_stock_kari = False
            break  # Exit the loop when not found any la

    # Determine the status based on out_of_stock
    if out_of_stock_kari:
        oos_maggi_kari = "Yes" #Out of stock
    else:
        oos_maggi_kari = "No" # In stock
    
        
    #SOV - Maggi Tomyam
    # Initialize the out_of_stock status as False
    out_of_stock_tomyam = True #Out of Stock

    # Check if any of the products are missing in the detected products
    for product in maggi_tomyam_to_check:
        if product in detected_products: #checkProduct ade dlm list
            # Set out_of_stock to False, bkn OOS
            out_of_stock_tomyam = False
            break  # Exit the loop when not found any la

    # Determine the status based on out_of_stock
    if out_of_stock_tomyam:
        oos_maggi_tomyam = "Yes" #Out of stock
    else:
        oos_maggi_tomyam = "No" # In stock
        
        
        
        
    #SOV- Nestle Koko
    # Check 
    out_of_stock_koko = True #Out of Stock
    
    for product in nestle_koko_to_check:
        if product in detected_products: #checkProduct ade dlm list
            # Set out_of_stock to False, bkn OOS
            out_of_stock_koko = False
            break  # Exit the loop when not found any la

    if out_of_stock_koko:
        oos_nestle_koko = "Yes" #Out of stock
    else:
        oos_nestle_koko = "No" # In stock
        
    #SOV- Nestle Milo
    # Check 
    out_of_stock_milo = True #Out of Stock
    
    for product in nestle_milo_to_check:
        if product in detected_products: #checkProduct ade dlm list
            # Set out_of_stock to False, bkn OOS
            out_of_stock_milo = False
            break  # Exit the loop when not found any la

    if out_of_stock_milo:
        oos_nestle_milo = "Yes" #Out of stock
    else:
        oos_nestle_milo = "No" # In stock
    
    #SOV- Nestle Star
    # Check 
    out_of_stock_star = True #Out of Stock
    
    for product in nestle_star_to_check:
        if product in detected_products: #checkProduct ade dlm list
            # Set out_of_stock to False, bkn OOS
            out_of_stock_star = False
            break  # Exit the loop when not found any la

    if out_of_stock_star:
        oos_nestle_star = "Yes" #Out of stock
    else:
        oos_nestle_star = "No" # In stock
    
    return oos_maggi_kari, oos_maggi_tomyam, oos_nestle_koko, oos_nestle_milo, oos_nestle_star
    
    
    
def out_of_stock_maggi(detected_products):
    # List of products to check for out-of-stock
    maggi_to_check = [
        "maggi kari unsorted", "maggi kari", "maggi tomyam", "maggi tomyamunsorted"
    ]
    
    # Initialize the out_of_stock status as False
    out_of_stock = True #Out of Stock

    # Check if any of the products are missing in the detected products
    for product in maggi_to_check:
        if product in detected_products: #checkProduct ade dlm list
            # Set out_of_stock to False, bkn OOS
            out_of_stock = False
            break  # Exit the loop when not found any la

    # Determine the status based on out_of_stock
    if out_of_stock:
        oos_maggi = "Yes" #Out of stock
    else:
        oos_maggi = "No" # In stock

    return oos_maggi

def out_of_stock_nestle(detected_products):
   
    nestle_to_check = [
        "nestle koko unsorted", "nestle koko", "nestle milo unsorted", "nestle milo",
        "nestle stars unsorted", "nestle stars"
    ]

    out_of_stock = True #Out of Stock

    # Check 
    for product in nestle_to_check:
        if product in detected_products: #checkProduct ade dlm list
            # Set out_of_stock to False, bkn OOS
            out_of_stock = False
            break  # Exit the loop when not found any la

    if out_of_stock:
        oos_nestle = "Yes" #Out of stock
    else:
        oos_nestle = "No" # In stock

    return oos_nestle

def complience_maggi(detected_products):
   
    maggi_to_check = [
        "maggi kari unsorted", "maggi tomyamunsorted"
    ]

    complience = False #organized

    # Check 
    for product in maggi_to_check:
        if product in detected_products: #checkProduct ade dlm list
            # Set complience to False, tak organized
            complience = True
            break  # Exit the loop when not found any la

    if complience:
        complience_maggi = "Non-Compliance" #not organized
    else:
        complience_maggi = "Compliance" # organized

    return complience_maggi

def complience_nestle(detected_products):
   
    nestle_to_check = [
        "nestle koko unsorted", "nestle milo unsorted", "nestle stars unsorted"
    ]

    complience = False #organized

    # Check 
    for product in nestle_to_check:
        if product in detected_products: #checkProduct ade dlm list
            # Set complience to False, tak organized
            complience = True
            break  # Exit the loop when not found any la

    if complience:
        complience_nestle = "Non-Compliance" #not organized
    else:
        complience_nestle = "Compliance" #organized

    return complience_nestle

def nestle_eye_level_check(detected_products, detected_boxes):
    # List of products to check for out-of-stock
    nestle_to_check = [
        "nestle koko unsorted", "nestle koko", "nestle milo unsorted", "nestle milo",
        "nestle stars unsorted", "nestle stars"
    ]
    # Initialize 
    product_yaxis = []
    # Initialize eye level
    nestle_eye_level_status = "Yes"

    #nestle
    # Check if any of the products are missing in the detected products
    for product in nestle_to_check:
        if product in detected_products: #checkProduct ade dlm list
            print("Product Detected:", product)
            # Check the coordinates for this product
            product_index = detected_products.index(product)
            product_box = detected_boxes[product_index]
            # Extract y_min and y_max values
            y_min, y_max = product_box[1], product_box[3]
            print("Coordinates for", product, ": y_min:", y_min, "y_max:", y_max)
            product_yaxis.append((y_min, y_max))  # Add y_min and y_max to the list

            # Assuming the boxes are in [x1, y1, x2, y2] format
            # Check if the product is NOT within the specified height range (2 meters)
            if  (500 < y_min <= 600) and (600 < y_max <= 750) : #takde kat coordinat ni
                nestle_eye_level_status = "Yes"  
            else:
                nestle_eye_level_status = "No" # not eye level
                
            
    return nestle_eye_level_status

def maggi_eye_level_check(detected_products, detected_boxes):
    # List of products to check for out-of-stock
    
    
    maggi_to_check = [
        "maggi kari unsorted", "maggi kari", "maggi tomyam", "maggi tomyamunsorted"
    ]
    
    product_yaxis = []
    # Initialize eye level
    maggi_eye_level_status = "Yes"
      
    #Maggi
    # Check if any of the products are missing in the detected products
    for product in maggi_to_check:
        if product in detected_products: #checkProduct ade dlm list
            print("Product Detected:", product)
             # Check the coordinates for this product
            product_index = detected_products.index(product)
            product_box = detected_boxes[product_index]
            # Extract y_min and y_max values
            y_min, y_max = product_box[1], product_box[3] #patut dia ambil y axis, tp kene ambil x axis sbb gmbr terbalik
            print("Coordinates for", product, ": y_min:", y_min, "y_max:", y_max)
            product_yaxis.append((y_min, y_max))  # Add y_min and y_max to the list

            # Assuming the boxes are in [x1, y1, x2, y2] format
            # Check if the product is NOT within the specified height range (2 meters)
            if  (500 < y_min <= 600) and (600 < y_max <= 750) : #takde kat coordinat ni
                maggi_eye_level_status = "Yes"  
            else:
                maggi_eye_level_status = "No"   # not eye level
                
            
    return maggi_eye_level_status



