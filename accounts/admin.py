import uuid
import random  # <--- Added import for random number generation
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# We assume 'Doctor' here is the Proxy User model from accounts/models.py
from .models import Doctor 
from appointments.models import Doctor as DoctorProfile 

# ========================================================
# 1. SPECIAL FORM FOR DOCTORS (With Specialization)
# ========================================================
class DoctorCreationForm(forms.ModelForm):
    # Minimal fields for account creation
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    
    # --- Specialization Dropdown ---
    specialization = forms.ChoiceField(
        choices=DoctorProfile.SPECIALIZATIONS, 
        required=True,
        label="Specialization",
        help_text="Select specialization. Department auto-updates."
    )

    class Meta:
        model = Doctor
        fields = ('email', 'first_name', 'last_name', 'password', 'specialization')

    def save(self, commit=True):
        user = super().save(commit=False)
        # 1. Set the password
        user.set_password(self.cleaned_data["password"])
        
        # 2. Force Role to Doctor
        user.role = 'doctor'
        
        # 3. Generate unique username (Format: d + 6 random digits + cb)
        # Example: d839201cb
        user.username = f"d{random.randint(100000, 999999)}cb"
        
        # 4. Set defaults to prevent Integrity Errors
        user.is_verified = True
        user.patient_id = None
        user.google_auth = False
        
        if commit:
            user.save()
            
            # 5. Save Specialization to the Doctor Profile
            if hasattr(user, 'doctor_profile'):
                profile = user.doctor_profile
                profile.specialization = self.cleaned_data['specialization']
                profile.save() # Triggers models.py auto-department logic
            else:
                DoctorProfile.objects.create(
                    user=user, 
                    specialization=self.cleaned_data['specialization']
                )
                
        return user

# ========================================================
# 2. DOCTOR ADMIN CONFIGURATION
# ========================================================
# FIX: Changed from admin.ModelAdmin to UserAdmin to fix UI issues
class DoctorAdmin(UserAdmin):
    # --- LINK TO YOUR CUSTOM BUTTON TEMPLATE ---
    # This matches the folder structure you created: templates/admin/accounts/doctoraccount/
    change_list_template = "admin/accounts/doctoraccount/change_list.html"
    
    add_form = DoctorCreationForm
    
    # List View Columns
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_specialization', 'is_verified')
    
    # Fields to display on the "Add User" page (Fixes the UI for adding)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password', 'specialization'),
        }),
    )

    # Filter to show only Doctors
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role='doctor')

    # Helper for List View
    def get_specialization(self, obj):
        if hasattr(obj, 'doctor_profile'):
            return obj.doctor_profile.specialization
        return "-"
    get_specialization.short_description = 'Specialization'

# ========================================================
# 3. STANDARD USER ADMIN (For Patients/Admin)
# ========================================================
class CustomUserAdmin(UserAdmin):
    ordering = ('-date_joined',)
    list_display = ('username', 'role', 'first_name', 'email')
    fieldsets = ((None, {'fields': ('username', 'password')}), 
                 ('Personal', {'fields': ('first_name', 'last_name', 'email', 'role')}))

# Register Models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Doctor, DoctorAdmin)