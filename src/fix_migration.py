#!/usr/bin/env python
"""
Fix migration by creating missing tables and marking migrations as applied
"""

import mysql.connector
from mysql.connector import Error

def fix_migration():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='admin123',
            database='healthcare_db'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("Creating missing tables...")
            
            # Create dashboard_appointmentfeedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_appointmentfeedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    appointment_id INT NOT NULL,
                    patient_id INT NOT NULL,
                    doctor_id INT NOT NULL,
                    rating INT CHECK (rating >= 1 AND rating <= 5),
                    feedback TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created dashboard_appointmentfeedback table")
            
            # Create dashboard_healthmetrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_healthmetrics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id INT NOT NULL,
                    weight DECIMAL(5,2),
                    height DECIMAL(5,2),
                    blood_pressure_systolic INT,
                    blood_pressure_diastolic INT,
                    heart_rate INT,
                    temperature DECIMAL(4,1),
                    recorded_date DATE NOT NULL,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created dashboard_healthmetrics table")
            
            # Create dashboard_medicationreminder table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_medicationreminder (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id INT NOT NULL,
                    medication_name VARCHAR(200) NOT NULL,
                    dosage VARCHAR(100),
                    frequency VARCHAR(100),
                    start_date DATE NOT NULL,
                    end_date DATE,
                    reminder_time TIME NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created dashboard_medicationreminder table")
            
            # Create dashboard_emergencycontact table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_emergencycontact (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    patient_id INT NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    relationship VARCHAR(50),
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    is_primary BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created dashboard_emergencycontact table")
            
            # Create dashboard_doctorscheduletemplate table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_doctorscheduletemplate (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT NOT NULL,
                    day_of_week INT NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    max_appointments INT DEFAULT 10,
                    is_available BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created dashboard_doctorscheduletemplate table")
            
            # Create dashboard_doctoravailabilityslot table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_doctoravailabilityslot (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT NOT NULL,
                    date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    is_available BOOLEAN DEFAULT TRUE,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created dashboard_doctoravailabilityslot table")
            
            # Create dashboard_doctorperformancemetrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_doctorperformancemetrics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT NOT NULL,
                    date DATE NOT NULL,
                    total_appointments INT DEFAULT 0,
                    completed_appointments INT DEFAULT 0,
                    cancelled_appointments INT DEFAULT 0,
                    average_rating DECIMAL(3,2),
                    patient_satisfaction_score DECIMAL(3,2),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created dashboard_doctorperformancemetrics table")
            
            # Create dashboard_prescriptiontemplate table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_prescriptiontemplate (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    doctor_id INT NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    medication_list JSON,
                    instructions TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created dashboard_prescriptiontemplate table")
            
            # Create dashboard_meetingreminder table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_meetingreminder (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    appointment_id INT NOT NULL UNIQUE,
                    reminder_10min_sent BOOLEAN DEFAULT FALSE,
                    reminder_5min_sent BOOLEAN DEFAULT FALSE,
                    reminder_2min_sent BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("✅ Created dashboard_meetingreminder table")
            
            print("\nMarking migrations as applied...")
            
            # Mark dashboard.0004 migration as applied
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('dashboard', '0004_alter_notification_category_meetingreminder', NOW())
                ON DUPLICATE KEY UPDATE applied = NOW()
            """)
            
            # Mark dashboard.0005 migration as applied
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES ('dashboard', '0005_prescriptiontemplate_medicationreminder_and_more', NOW())
                ON DUPLICATE KEY UPDATE applied = NOW()
            """)
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print("✅ All missing tables created and migrations fixed!")
            print("Now you can delete users from the admin panel.")
            
    except Error as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_migration()
