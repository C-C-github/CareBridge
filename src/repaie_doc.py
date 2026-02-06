import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthcare_system.settings")
django.setup()

from appointments.models import Department, Doctor

SPEC_TO_DEPT = {
    "General Physician": "General Medicine",
    "Cardiologist": "Cardiology",
    "Cardiothoracic Surgeon": "Cardiothoracic Surgery",
    "Dermatologist": "Dermatology",
    "Orthopedic": "Orthopedics",
    "Neurologist": "Neurology",
    "Pediatrician": "Pediatrics",
    "Psychiatrist": "Psychiatry",
    "Dentist": "Dentistry",
    "ENT": "ENT",
    "ENT Surgeon": "ENT",
    "Gynecologist": "Obstetrics & Gynecology",
    "Urologist": "Urology",
    "Oncologist": "Oncology",
    "Endocrinologist": "Endocrinology",
    "Ophthalmologist": "Ophthalmology",
    "Pulmonologist": "Pulmonology",
    "Gastroenterologist": "Gastroenterology",
    "Rheumatologist": "Rheumatology",
    "Nephrologist": "Nephrology",
    "Radiologist": "Radiology",
    "Anesthesiologist": "Anesthesiology",
    "General Surgeon": "General Surgery",
    "Plastic Surgeon": "Plastic Surgery",
    "Vascular Surgeon": "Vascular Surgery",
}

print("\nCreating missing departments...")
for dept in set(SPEC_TO_DEPT.values()):
    Department.objects.get_or_create(name=dept)

print("Departments ready.\n")

print("Fixing doctor department assignments...")
for doctor in Doctor.objects.all():
    dept_name = SPEC_TO_DEPT.get(doctor.specialization)

    if not dept_name:
        print(f"⚠ No mapping for Dr. {doctor.user.username} ({doctor.specialization})")
        continue

    dept_obj = Department.objects.get(name=dept_name)

    if doctor.department != dept_obj:
        doctor.department = dept_obj
        doctor.save()
        print(f"✔ Updated Dr. {doctor.user.username} → {dept_name}")

print("\nRepair completed successfully.")
