#!/usr/bin/env python
"""
Clear existing MySQL tables for fresh migration
"""

import pymysql
from pymysql import Error

def clear_mysql_tables():
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host='localhost',
            user='admin',
            password='admin123',
            database='healthcare_db'
        )
        
        if connection.open:
            cursor = connection.cursor()
            
            # Get all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"Found {len(tables)} tables to clear...")
            
            # Drop all tables
            for table in tables:
                table_name = table[0]
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"Dropped table: {table_name}")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print("\n✅ All tables cleared successfully!")
            print("You can now run: python manage.py migrate")
            
    except Error as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    clear_mysql_tables()
