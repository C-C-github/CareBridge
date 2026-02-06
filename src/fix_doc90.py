import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthcare_system.settings")
django.setup()

from appointments.models import Doctor

# FIRST PRIORITY specialization per department
DEPT_PRIORITY_SPEC = {
    "General Medicine": "General Physician",
    "Cardiology": "Cardiologist",
    "Cardiothoracic Surgery": "Cardiothoracic Surgeon",
    "Dermatology": "Dermatologist",
    "Orthopedics": "Orthopedic",
    "Neurology": "Neurologist",
    "Neurosurgery": "Neurosurgeon",
    "Pediatrics": "Pediatrician",
    "Psychiatry": "Psychiatrist",
    "Dentistry": "Dentist",
    "ENT": "ENT",
    "Obstetrics & Gynecology": "Gynecologist",
    "Urology": "Urologist",
    "Oncology": "Oncologist",
    "Endocrinology": "Endocrinologist",
    "Ophthalmology": "Ophthalmologist",
    "Pulmonology": "Pulmonologist",
    "Gastroenterology": "Gastroenterologist",
    "Rheumatology": "Rheumatologist",
    "Nephrology": "Nephrologist",
    "Radiology": "Radiologist",
    "Anesthesiology": "Anesthesiologist",
    "General Surgery": "General Surgeon",
    "Plastic Surgery": "Plastic Surgeon",
    "Vascular Surgery": "Vascular Surgeon",
    "Rehabilitation Medicine": "Physiotherapist",
    "Emergency Medicine": "Emergency Physician",
    "Pathology": "Pathologist",
    "Geriatrics": "Geriatrician",
    "Infectious Diseases": "Infectious Disease Specialist",
}

print("\n🔄 Forcing specialization update using priority mapping...\n")

updated = 0
skipped = 0

for doctor in Doctor.objects.select_related("department"):
    if not doctor.department:
        skipped += 1
        continue

    dept_name = doctor.department.name
    priority_spec = DEPT_PRIORITY_SPEC.get(dept_name)

    if not priority_spec:
        print(f"⚠ No priority spec for department: {dept_name}")
        skipped += 1
        continue

    if doctor.specialization != priority_spec:
        doctor.specialization = priority_spec
        doctor.save(update_fields=["specialization"])
        print(f"✔ Updated Dr. {doctor.user.username}: {dept_name} → {priority_spec}")
        updated += 1
    else:
        skipped += 1

print(f"\n✅ Done. Updated: {updated}, Skipped: {skipped}\n")
