import os
import django

# ✅ CHANGE THIS if your project settings module is different
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthcare_system.settings")
django.setup()
from appointments.models import Doctor, Department

# 1) If department name is wrong (a specialization), move to correct canonical department
DEPT_RENAME = {
    "Consultant Psychiatrist": "Psychiatry",
    "Clinical Psychologist": "Psychiatry",
    "Psychiatrist": "Psychiatry",

    "Pulmonologist": "Pulmonology",
    "Oncologist": "Oncology",
    "Medical Oncologist": "Oncology",

    "Neurologist": "Neurology",
}

# 2) Department -> default specialization (what you asked: "from dept you need spec")
DEPT_TO_SPEC = {
    "Rehabilitation Medicine": "Rehab Consultant",
    "Psychiatry": "Consultant Psychiatrist",
    "Emergency Medicine": "Emergency Consultant",
    "Pathology": "Laboratory Consultant",
    "Radiology": "Imaging Consultant",
    "Plastic Surgery": "Plastic Surgeon",
    "Rheumatology": "Rheumatologist",
    "Anesthesiology": "Anesthesiologist",
    "Ent": "ENT Specialist",
    "Endocrinology": "Endocrinologist",
    "Neurosurgery": "Neurosurgeon",
    "Urology": "Urologist",
    "Gastroenterology": "Gastroenterologist",
    "Dermatology": "Dermatologist",
    "Obstetrics & Gynecology": "Gynecologist",
    "Pulmonology": "Pulmonologist",
    "Oncology": "Medical Oncologist",
    "Nephrology": "Nephrologist",
    "Cardiothoracic Surgery": "Cardiothoracic Surgeon",
    "General Surgery": "General Surgeon",
    "Orthopedics": "Orthopedic",
    "Neurology": "Neurologist",
    "Cardiology": "Cardiologist",
    "Pediatrics": "Pediatrician",
    "General Medicine": "General Physician",
    "Geriatrics": "Geriatrician",
    "Infectious Diseases": "Infectious Disease Specialist",
    "Ophthalmology": "Ophthalmologist",
}

def is_blank_spec(value: str | None) -> bool:
    if value is None:
        return True
    v = str(value).strip()
    return v in ("", "-", "—")

# Ensure canonical departments exist
for canon_dept in set(DEPT_RENAME.values()) | set(DEPT_TO_SPEC.keys()):
    Department.objects.get_or_create(name=canon_dept)

dept_fixed = 0
spec_fixed = 0

for d in Doctor.objects.select_related("department"):
    if not d.department:
        continue

    dept_name = (d.department.name or "").strip()

    # A) Fix wrong department names (specialization-like departments)
    if dept_name in DEPT_RENAME:
        new_dept_name = DEPT_RENAME[dept_name]
        new_dept = Department.objects.get(name=new_dept_name)
        if d.department_id != new_dept.id:
            d.department = new_dept
            dept_fixed += 1
        dept_name = new_dept_name

    # B) Fix specialization from department if specialization is blank
    if is_blank_spec(d.specialization):
        mapped_spec = DEPT_TO_SPEC.get(dept_name)
        if mapped_spec:
            d.specialization = mapped_spec
            spec_fixed += 1

    d.save(update_fields=["department", "specialization"])

print("✅ Department fixed:", dept_fixed)
print("✅ Specialization fixed:", spec_fixed)