import os
import django
import random
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthcare_system.settings")
django.setup()

from appointments.models import Doctor

DEFAULT_EXP = (2, 20)
DEFAULT_FEE = (400, 1500)

updated = 0

for d in Doctor.objects.all():
    exp = random.randint(*DEFAULT_EXP)
    fee = random.choice(range(DEFAULT_FEE[0], DEFAULT_FEE[1] + 1, 50))

    d.experience_years = exp
    d.consultation_fee = Decimal(str(fee))
    d.save(update_fields=["experience_years", "consultation_fee"])

    updated += 1

print(f"✅ Updated {updated} doctors with random experience & fee")
