import mysql.connector
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

# Database connection parameters
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

def setup_database():
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            port=db_port
        )
        
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists.")
        
        # Use the database
        cursor.execute(f"USE {db_name}")
        
        # Read and execute SQL script
        with open('dataset.sql', 'r') as file:
            sql_script = file.read()
            
            # Split the script into individual statements
            statements = sql_script.split(';')
            
            # Execute each statement
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
            
            conn.commit()
            print("Database schema and data imported successfully.")
        
        cursor.close()
        conn.close()
        print("Database setup completed successfully.")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database() 