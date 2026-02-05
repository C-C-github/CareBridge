#!/usr/bin/env python
"""
MySQL Database Setup Script for Healthcare Project
Run this script to create the database and user
"""

import mysql.connector
from mysql.connector import Error

def setup_mysql_database():
    try:
        # Connect to MySQL server (without database)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Use root user for initial setup
            password=''  # Add your MySQL root password if needed
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS healthcare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("Database 'healthcare_db' created or already exists")
            
            # Create user if not exists
            cursor.execute("CREATE USER IF NOT EXISTS 'admin'@'localhost' IDENTIFIED BY 'admin123'")
            print("User 'admin' created or already exists")
            
            # Grant privileges
            cursor.execute("GRANT ALL PRIVILEGES ON healthcare_db.* TO 'admin'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            print("Privileges granted to user 'admin'")
            
            # Test connection with new user
            cursor.execute("USE healthcare_db")
            print("Successfully connected to healthcare_db database")
            
            cursor.close()
            connection.close()
            
            print("\n✅ MySQL setup completed successfully!")
            print("Database: healthcare_db")
            print("User: admin")
            print("Password: admin123")
            print("Host: localhost")
            print("Port: 3306")
            
    except Error as e:
        print(f"❌ Error: {e}")
        print("\nPlease ensure:")
        print("1. MySQL server is running")
        print("2. You have correct MySQL root password")
        print("3. MySQL is installed on your system")

if __name__ == "__main__":
    setup_mysql_database()
