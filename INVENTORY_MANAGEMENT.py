import mysql.connector
from mysql.connector import Error
import pandas as pd
import datetime
import os
import time
from tabulate import tabulate

pw = "8123"  # Replace with your actual MySQL root password
db = "Inventory"

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def check_schema_exists(connection):
    query = """
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.SCHEMATA
    WHERE SCHEMA_NAME = 'inventory';
    """
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    return result[0] > 0


def execute_querry(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"Error: {e}")


def table_create_exits():
    def create_trigger_insertion():
        try:
            q_use_db = "USE inventory;"
            q_create_trigger = """
                CREATE TRIGGER IF NOT EXISTS after_sale_insert
                AFTER INSERT ON sales
                FOR EACH ROW
                BEGIN
                    UPDATE stocks
                    SET quantity = quantity - NEW.quantity WHERE pid = NEW.pid;
                END;
            """
            execute_querry(connection, q_use_db)  
            execute_querry(connection, q_create_trigger)
            print("Insertion trigger created successfully")
        except Error as e:
            print(f"The error '{e}' occurred")

    def create_trigger_deletion():
        try:
            q_use_db = "USE inventory;"
            q_create_trigger = """
                    CREATE TRIGGER IF NOT EXISTS after_sale_delete
                    AFTER DELETE ON sales
                    FOR EACH ROW
                    BEGIN
                        UPDATE stocks
                        SET quantity = quantity + OLD.quantity WHERE pid = OLD.pid;
                    END;
            """
            execute_querry(connection, q_use_db)  
            execute_querry(connection, q_create_trigger)
            print("Deletion trigger created successfully")
        except Error as e:
            print(f"The error '{e}' occurred")
    
    def create_o_deletion():
        try:
            q_use_db = "USE inventory;"
            q_create_trigger = """
                CREATE TRIGGER IF NOT EXISTS delete_product_if_quantity_zero
                AFTER UPDATE ON inventory.stocks
                FOR EACH ROW
                BEGIN
                    IF NEW.quantity = 0 THEN
                        DELETE FROM inventory.products WHERE pid = NEW.pid;
                        DELETE FROM inventory.stocks WHERE pid = NEW.pid;
                    END IF;
                END;
            """
            execute_querry(connection, q_use_db)  
            execute_querry(connection, q_create_trigger)
            print("Zero quantity deletion trigger created successfully")
        except Error as e:
            print(f"The error '{e}' occurred")
            
    def create_tables():
        try:
            q_use_db = "USE inventory;"
            execute_querry(connection, q_use_db)
            
            q_create_stocks = """
            CREATE TABLE IF NOT EXISTS stocks(
                pid int primary key,
                pname varchar(255) unique,
                quantity int
            )"""
            execute_querry(connection, q_create_stocks)
            print("Stocks table created successfully")

            q_create_products = """
            CREATE TABLE IF NOT EXISTS products(
                pid int primary key,
                pname varchar(255) unique,
                pprice int
            )"""
            execute_querry(connection, q_create_products)
            print("Products table created successfully")

            q_create_sales = """
            CREATE TABLE IF NOT EXISTS sales(
                id int primary key,
                date_ordered date,
                name varchar(255) not null,
                pid int not null,
                pname varchar(255) not null, 
                pprice int,   
                quantity int not null,
                total int
            )"""
            execute_querry(connection, q_create_sales)
            print("Sales table created successfully")

        except Error as e:
            print(f"The error '{e}' occurred")

    # Create tables first
    create_tables()

    # Then create triggers
    create_trigger_insertion()
    create_trigger_deletion()
    create_o_deletion()


def fetch_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error is '{e}'")

             
def insert_stock_products():
    while True:
        print("ENTERING INTO STOCKS AND PRODUCTS")
        try:
            query = "SELECT COUNT(pid) AS total_id FROM inventory.stocks;"
            c_id = fetch_query(connection, query)
            id = c_id[0][0] + 1
            pname = input("Enter product name: ")
            quantity = int(input("Enter quantity: "))
            pprice = int(input("Enter price: "))
            query = f"""INSERT INTO inventory.stocks (pid, pname, quantity)
            VALUES ({id}, '{pname}', {quantity});"""
            execute_querry(connection, query)
            query = f"""
            INSERT INTO inventory.products (pid, pname, pprice)
            VALUES ({id}, '{pname}', {pprice});
            """
            execute_querry(connection, query)
            print("Product inserted successfully.")
            clear(2)
        except Error as e:
            print(f"Error: {e}")
            clear(2)
        except ValueError:
            print("Invalid input. Please enter a valid ID or '**' to exit.")
            clear(2)

    
def insert_sales():
    while True:
        try:
            print("ENTERING INTO SALES")
            query = "SELECT COUNT(pid) AS total_id FROM inventory.sales;"
            c_id = fetch_query(connection, query)
            id = c_id[0][0] + 1
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            name = input("Enter customer name (or '**' to exit): ")
            if name == "**":
                print("Exiting.")
                break
            pid = int(input("Enter product ID: "))
            query = f"SELECT pname FROM inventory.stocks WHERE pid = {pid};"
            pname_results = fetch_query(connection, query)  
            if not pname_results:
                print("No product found with the given ID.")
                continue
            pname = pname_results[0][0]
            query = f"SELECT pprice FROM inventory.products WHERE pid = {pid};"
            pprice_results = fetch_query(connection, query)  
            if not pprice_results:
                print("No product found with the given ID.")
                continue
            pprice = pprice_results[0][0]  
            while True:
                try:
                    quantity = int(input("Enter quantity: "))
                    total = pprice * quantity
                    break 
                except ValueError:
                    print("Invalid input. Please enter a numeric value for the quantity.")
            query = f"""
            INSERT INTO inventory.sales 
            VALUES ({id}, '{date}', '{name}', {pid}, '{pname}', {pprice}, {quantity}, {total});
            """
            execute_querry(connection, query)
            print("Sales inserted successfully.")
            clear(2)
        except Error as e:
            print(f"Error: {e}")
            clear(2)


def read_stocks(connection, query):
    cursor = connection.cursor()
    result = None
    from_db = []
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        for result in results:
            result = list(result)
            from_db.append(result)
        columns = ["PID", "Product Name", "Quantity"]
        print(tabulate(from_db, headers=columns, tablefmt="grid"))
    except Error as e:
        print(f"The error is '{e}'")

def read_products(connection, query):
    cursor = connection.cursor()
    result = None
    from_db = []
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        for result in results:
            result = list(result)
            from_db.append(result)
        columns = ["PID", "Product Name", "Price"]
        print(tabulate(from_db, headers=columns, tablefmt="grid"))
    except Error as e:
        print(f"The error is '{e}'")

def read_sales(connection, query):
    cursor = connection.cursor()
    result = None
    from_db = []
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        for result in results:
            result = list(result)
            from_db.append(result)
        columns = ["ID", "Date", "Name", "PID", "Product Name", "Price", "Quantity", "Total"]
        print(tabulate(from_db, headers=columns, tablefmt="grid"))
    except Error as e:
        print(f"The error is '{e}'")

def display_stocks():
    print("Table is displayed")
    while True:
        read_stocks(connection, "SELECT * FROM inventory.stocks")
        print("Press Enter to continue or 'q' to quit...\n")
        if input().lower() == 'q':
            break

def display_products():
    print("Table is displayed")
    while True:
        read_products(connection, "SELECT * FROM inventory.products")
        print("Press Enter to continue or 'q' to quit...\n")
        if input().lower() == 'q':
            break
        
def display_sales():
    print("Table is displayed")
    while True:
        read_sales(connection, "SELECT * FROM inventory.sales")
        print("Press Enter to continue or 'q' to quit...\n")
        if input().lower() == 'q':
            break


def stock_update():
    while True:
        value_id = None
        new_value = None
        try: 
            print("UPDATING STOCKS")
            value_id = int(input("Enter the id of the row you want to update (or '000' to exit): "))
            if value_id == 000:
                print("Exiting.")
                break
            new_value = int(input("Enter the new quantity: "))
            query = f"""
            UPDATE inventory.stocks
            SET quantity = {new_value}
            WHERE pid = {value_id};
            """
            execute_querry(connection, query)
            print("Stock updated successfully.")
            clear(2)
        except ValueError:
            print("Invalid input. The input should be an integer.")
            clear(2)


def products_update():
    while True:
        value_id = None
        new_value = None
        try: 
            print("UPDATING PRODUCTS")
            value_id = int(input("Enter the id of the row you want to update (or '000' to exit): "))
            if value_id == 000:
                print("Exiting.")
                break
            new_value = int(input("Enter the new price: "))
            query = f"""
            UPDATE inventory.products
            SET pprice = {new_value}  
            WHERE pid = {value_id};
            """
            execute_querry(connection, query)
            print("Product updated successfully.")
            clear(2)
        except ValueError:
            print("Invalid input. The input should be an integer.")   
            clear(2)             


def delete_value():
    tb_name = None
    value_id = None
    while True:
        print("DELETING VALUES")
        table = input("Choose a table to delete\n1. stocks\n2. products\n3. sales\n(or '000' to exit): ")
        if table == "000":
            print("Exiting.")
            break
        elif table in ["1", "2", "3"]:
            if table == "1":
                tb_name = "stocks"
            elif table == "2":
                tb_name = "products"
            elif table == "3":
                tb_name = "sales"
        else:
            print("Invalid choice, please try again.")
            continue
        try:
            value_id = int(input("Enter the id of the row you want to delete: "))
            if tb_name == "products" or tb_name == "stocks":
                query = f"""
                DELETE FROM inventory.stocks WHERE pid = {value_id};
                """
                execute_querry(connection, query)
                query = f"""
                DELETE FROM inventory.products WHERE pid = {value_id};
                """
                execute_querry(connection, query)
            else:
                query = f"""
                DELETE FROM inventory.{tb_name} WHERE id = {value_id};
                """
                execute_querry(connection, query)
            clear(2)
        except ValueError:
            print("Invalid input. Please enter a valid ID.")  
            clear(2)  


def type_animation(text):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(0.1)


def clear(n):
    time.sleep(n)
    os.system('cls' if os.name == 'nt' else 'clear')


def admin_switch(choice):
    match choice:
        case 1:
            clear(1)
            insert_sales()
            clear(2)
        case 2:
            clear(1)
            insert_stock_products()
            clear(2)
        case 3:
            clear(1)
            display_stocks()
            clear(0.1)
        case 4:
            clear(1)
            display_products()
            clear(0.1)
        case 5:
            clear(1)
            display_sales()
            clear(0.1)
        case 6:
            clear(1)
            stock_update()
            clear(2)
        case 7:
            clear(1)
            products_update()
            clear(2)
        case 8:
            clear(1)
            delete_value()
            clear(2)
        case 9:
            clear(1)
            print("Exiting the program. Goodbye!")
            exit()
        case _:
            print("Invalid choice. Please choose again.")


# Main execution
connection = create_server_connection("localhost", "root", pw)

if not check_schema_exists(connection):
    query = "CREATE DATABASE IF NOT EXISTS Inventory"
    create_database(connection, query)
    print("Database 'Inventory' created.")

# Ensure we're connected to the Inventory database
connection = create_db_connection("localhost", "root", pw, "Inventory")

# Create tables and triggers
table_create_exits()

clear(0.01)
# ... (previous code remains the same)


# Main execution
connection = create_server_connection("localhost", "root", pw)

if not check_schema_exists(connection):
    query = "CREATE DATABASE IF NOT EXISTS Inventory"
    create_database(connection, query)
    print("Database 'Inventory' created.")

# Ensure we're connected to the Inventory database
connection = create_db_connection("localhost", "root", pw, "Inventory")

# Create tables and triggers
table_create_exits()

clear(0.01)

type_animation(f'\033[34m WELCOME TO INVENTORY MANAGEMENT \033[0m')
for i in range(3):
    print("\n")
    type_animation(f'\033[33m BOOTING UP..... \033[0m\n')
    clear(0.1)
time.sleep(1)
clear(0.01)

while True:
    type_animation(f'\033[32m ENTER YOUR PASSWORD: \033[0m')
    password = input()
    if password == "admin":
        clear(0.1)
        while True:
            print("""\033[96m
WELCOME ADMIN TO INVENTORY MANAGEMENT SYSTEM\n 
1. INSERT SALES
2. INSERT A PRODUCT
3. CHECK EXISTING STOCKS
4. CHECK THE CURRENT PRICE
5. CHECK THE CURRENT SALES
6. UPDATE THE PRODUCT QUANTITY
7. UPDATE THE PRODUCT PRICE
8. DELETE AN ENTRY
9. Exit
\033[0m
 """)
            try:
                choice = int(input("\033[92m Enter your choice: \033[0m"))
                admin_switch(choice)
                if choice == 9:
                    break
            except ValueError:
                print("\033[31m Invalid input. Please enter a number. \033[0m")
        break  # Exit the main loop if admin chooses to exit
    else:
        print("\033[31m Invalid password. Please try again. \033[0m")
