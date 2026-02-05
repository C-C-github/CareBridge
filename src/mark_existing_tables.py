#!/usr/bin/env python
"""
Mark existing MySQL tables as applied in Django migrations
"""

import os
import sys
import django
from django.conf import settings
from django.db import connection

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_system.settings')
django.setup()

def mark_existing_tables():
    """Mark existing tables as applied in Django migrations"""
    
    # List of migration files to mark as applied
    migrations_to_mark = [
        ('accounts', '0001_initial'),
        ('accounts', '0002_customuser_aadhaar_card_customuser_is_verified_and_more'),
        ('accounts', '0003_remove_customuser_aadhaar_card_and_more'),
        ('accounts', '0004_doctor_remove_customuser_google_auth_and_more'),
        ('accounts', '0005_alter_customuser_id'),
        ('appointments', '0001_initial'),
        ('appointments', '0002_appointment_meeting_link'),
        ('appointments', '0003_alter_appointment_options_appointment_completed_at_and_more'),
        ('appointments', '0004_doctor_available_days_doctor_available_time_and_more'),
        ('appointments', '0005_alter_appointment_meeting_link_and_more'),
        ('appointments', '0006_alter_appointment_meeting_link_and_more'),
        ('appointments', '0007_alter_appointment_id_alter_department_id_and_more'),
        ('appointments', '0008_doctor_doctor_id'),
        ('dashboard', '0001_initial'),
        ('dashboard', '0002_alter_auditlog_options_auditlog_ip_address_and_more'),
        ('dashboard', '0003_alter_auditlog_id_alter_notification_id'),
        ('dashboard', '0004_alter_notification_category_meetingreminder'),
        ('dashboard', '0005_prescriptiontemplate_medicationreminder_and_more'),
        ('records', '0001_initial'),
        ('records', '0002_medicalreport_delete_medicalrecord'),
        ('records', '0003_remove_medicalreport_description_and_more'),
        ('records', '0004_alter_medicalreport_id'),
        ('sessions', '0001_initial'),
        ('admin', '0001_initial'),
        ('admin', '0002_logentry_remove_auto_add'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('auth', '0001_initial'),
        ('auth', '0002_alter_permission_name_max_length'),
        ('auth', '0003_alter_user_email_max_length'),
        ('auth', '0004_alter_user_username_opts'),
        ('auth', '0005_alter_user_last_login_null'),
        ('auth', '0006_require_contenttypes_0002'),
        ('auth', '0007_alter_validators_add_error_messages'),
        ('auth', '0008_alter_user_username_max_length'),
        ('auth', '0009_alter_user_last_name_max_length'),
        ('auth', '0010_alter_group_name_max_length'),
        ('auth', '0011_update_proxy_permissions'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]
    
    with connection.cursor() as cursor:
        for app, migration in migrations_to_mark:
            try:
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied) 
                    VALUES (%s, %s, NOW())
                    ON DUPLICATE KEY UPDATE applied = NOW()
                """, [app, migration])
                print(f"✅ Marked {app}.{migration} as applied")
            except Exception as e:
                print(f"❌ Failed to mark {app}.{migration}: {e}")
        
        print("\n🎉 Migration marking completed!")
        print("Now you can run: python manage.py migrate")

if __name__ == "__main__":
    mark_existing_tables()
