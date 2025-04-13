import mysql.connector
from dotenv import load_dotenv
import os
import sys
import pandas as pd

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
            port=int(db_port) if db_port else 3306
        )
        
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists.")
        
        # Use the database
        cursor.execute(f"USE {db_name}")
        
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS svcr_startups")
        cursor.execute("DROP TABLE IF EXISTS crunchbase")
        
        # Create startupticker table with larger column sizes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS svcr_startups (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(500),
            funding_year INT,
            funding_amount DECIMAL(20,2),
            canton VARCHAR(200),
            sector VARCHAR(500),
            funding_type VARCHAR(200),
            source VARCHAR(100)
        )
        """)
        print("Created svcr_startups table")
        
        # Create crunchbase table with larger column sizes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS crunchbase (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company_name VARCHAR(500),
            founded_year INT,
            total_funding DECIMAL(20,2),
            location VARCHAR(500),
            industry VARCHAR(500),
            funding_rounds INT,
            last_funding_date DATE
        )
        """)
        print("Created crunchbase table")
        
        # Import startupticker data
        print("Importing startupticker data...")
        df_startupticker = pd.read_excel("../data/Data-startupticker.xlsx")
        for _, row in df_startupticker.iterrows():
            sql = """INSERT INTO svcr_startups 
                    (company_name, funding_year, funding_amount, canton, sector, funding_type, source) 
                    VALUES (%s, %s, %s, %s, %s, %s, 'startupticker')"""
            values = (
                str(row.get('Company Name', ''))[:500],
                int(row.get('Year', 0)) if pd.notna(row.get('Year')) else None,
                float(row.get('Amount', 0)) if pd.notna(row.get('Amount')) else None,
                str(row.get('Canton', ''))[:200],
                str(row.get('Sector', ''))[:500],
                str(row.get('Type', ''))[:200]
            )
            cursor.execute(sql, values)
        conn.commit()
        print("Startupticker data imported successfully")
        
        # Import crunchbase data
        print("Importing crunchbase data...")
        df_crunchbase = pd.read_excel("../data/Data-crunchbase.xlsx")
        for _, row in df_crunchbase.iterrows():
            sql = """INSERT INTO crunchbase 
                    (company_name, founded_year, total_funding, location, industry, funding_rounds, last_funding_date) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            values = (
                str(row.get('Company Name', ''))[:500],
                int(row.get('Founded Year', 0)) if pd.notna(row.get('Founded Year')) else None,
                float(row.get('Total Funding', 0)) if pd.notna(row.get('Total Funding')) else None,
                str(row.get('Location', ''))[:500],
                str(row.get('Industry', ''))[:500],
                int(row.get('Funding Rounds', 0)) if pd.notna(row.get('Funding Rounds')) else None,
                row.get('Last Funding Date') if pd.notna(row.get('Last Funding Date')) else None
            )
            cursor.execute(sql, values)
        conn.commit()
        print("Crunchbase data imported successfully")
        
        cursor.close()
        conn.close()
        print("Database setup completed successfully.")
        
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database() 