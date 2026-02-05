from django.contrib import admin
from .models import Appointment, Doctor, Department

class DoctorAdmin(admin.ModelAdmin):
    # Show these columns in the list view
    list_display = ('__str__', 'specialization', 'department', 'experience_years', 'is_available')
    
    # Filters on the right side
    list_filter = ('specialization', 'is_available')
    
    # Make 'department' read-only in the edit form so admins don't manually change it
    readonly_fields = ('department',)
    
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Professional Details', {
            'fields': ('specialization', 'department', 'qualification', 'experience_years', 'consultation_fee')
        }),
        ('Availability', {
            'fields': ('is_available', 'available_days', 'available_time')
        }),
    )

admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Appointment)
admin.site.register(Department)