import uuid
import random
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    
    # 1. ALLOW NULLS: Critical
    patient_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # 2. Logic: If NOT a patient, force patient_id to be None
        if self.role != 'patient':
            self.patient_id = None
        
        # 3. Logic: Generate Patient ID
        elif self.role == 'patient' and not self.patient_id:
            while True:
                new_id = f"P-{uuid.uuid4().hex[:6].upper()}"
                if not CustomUser.objects.filter(patient_id=new_id).exists():
                    self.patient_id = new_id
                    break

        # 4. Logic: Generate Doctor ID (d...cb)
        if self.role == 'doctor':
            self.is_verified = True
            if not self.username or self.username.startswith('temp_'):
                unique_found = False
                while not unique_found:
                    random_digits = random.randint(100000, 999999)
                    new_username = f"d{random_digits}cb"
                    if not CustomUser.objects.filter(username=new_username).exists():
                        self.username = new_username
                        unique_found = True
            
        super().save(*args, **kwargs)

# ==========================================
# 5. NEW: The Doctor Proxy Model
# ==========================================
class Doctor(CustomUser):
    class Meta:
        proxy = True
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'