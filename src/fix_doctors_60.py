import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthcare_system.settings")
django.setup()

from appointments.models import Doctor, Department

# Specialization ➜ Correct Department
SPEC_TO_DEPT = {
    "General Physician": "General Medicine",
    "Cardiologist": "Cardiology",
    "Cardiothoracic Surgeon": "Cardiothoracic Surgery",
    "Dermatologist": "Dermatology",
    "Cosmetologist": "Dermatology",
    "Orthopedic": "Orthopedics",
    "Orthopedic Surgeon": "Orthopedics",
    "Spine Surgeon": "Orthopedics",
    "Neurologist": "Neurology",
    "Neuro Consultant": "Neurology",
    "Neurosurgeon": "Neurosurgery",
    "Pediatrician": "Pediatrics",
    "Psychiatrist": "Psychiatry",
    "Consultant Psychiatrist": "Psychiatry",
    "Clinical Psychologist": "Psychiatry",
    "Dentist": "Dentistry",
    "ENT": "ENT",
    "ENT Surgeon": "ENT",
    "ENT Specialist": "ENT",
    "Ent Surgeon": "ENT",
    "Gynecologist": "Obstetrics & Gynecology",
    "Obstetrician": "Obstetrics & Gynecology",
    "Urologist": "Urology",
    "Uro-Oncologist": "Urology",
    "Oncologist": "Oncology",
    "Medical Oncologist": "Oncology",
    "Endocrinologist": "Endocrinology",
    "Diabetologist": "Endocrinology",
    "Thyroid Specialist": "Endocrinology",
    "Ophthalmologist": "Ophthalmology",
    "Pulmonologist": "Pulmonology",
    "Gastroenterologist": "Gastroenterology",
    "GI Surgeon": "Gastroenterology",
    "Gi Surgeon": "Gastroenterology",
    "Hepatologist": "Gastroenterology",
    "Rheumatologist": "Rheumatology",
    "Arthritis Specialist": "Rheumatology",
    "Nephrologist": "Nephrology",
    "Nephrology Consultant": "Nephrology",
    "Radiologist": "Radiology",
    "Imaging Consultant": "Radiology",
    "Anesthesiologist": "Anesthesiology",
    "Pain Specialist": "Anesthesiology",
    "General Surgeon": "General Surgery",
    "Plastic Surgeon": "Plastic Surgery",
    "Hand Surgeon": "Plastic Surgery",
    "Vascular Surgeon": "Vascular Surgery",
    "Physiotherapist": "Rehabilitation Medicine",
    "Rehabilitation Specialist": "Rehabilitation Medicine",
    "Rehab Consultant": "Rehabilitation Medicine",
    "Emergency Physician": "Emergency Medicine",
    "Emergency Consultant": "Emergency Medicine",
    "Pathologist": "Pathology",
    "Laboratory Consultant": "Pathology",
    "Geriatrician": "Geriatrics",
    "Infectious Disease Specialist": "Infectious Diseases",
}

print("\n🔧 Normalizing doctor departments...\n")

for doctor in Doctor.objects.select_related("department"):
    if not doctor.department:
        continue

    current_dept_name = doctor.department.name

    # If department name is actually a specialization, fix it
    corrected_dept = SPEC_TO_DEPT.get(current_dept_name)

    if corrected_dept:
        dept_obj, _ = Department.objects.get_or_create(name=corrected_dept)
        doctor.department = dept_obj
        doctor.save(update_fields=["department"])
        print(f"✔ Fixed Department: {current_dept_name} → {corrected_dept}")

print("\n🎯 Now syncing specialization with corrected departments...\n")

# Department ➜ Default Specialization
DEPT_TO_SPEC = {v: k for k, v in SPEC_TO_DEPT.items()}

for doctor in Doctor.objects.select_related("department"):
    if not doctor.department:
        continue

    dept_name = doctor.department.name
    correct_spec = DEPT_TO_SPEC.get(dept_name)

    if correct_spec and doctor.specialization != correct_spec:
        doctor.specialization = correct_spec
        doctor.save(update_fields=["specialization"])
        print(f"✔ Fixed Specialization for Dr. {doctor.user.username} → {correct_spec}")

print("\n✅ Database normalization complete.\n")
