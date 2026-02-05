from django.urls import path
from . import views

urlpatterns = [
    # Doctor-facing: upload report for a specific appointment
    path('doctor/upload/<int:appointment_id>/', views.upload_report_view, name='doctor_upload_report'),
    path('doctor/report/<int:report_id>/edit/', views.edit_report_view, name='doctor_edit_report'),

    # Patient-facing report features (read-only)
    path('my-reports/', views.patient_reports_view, name='patient_reports'),
    path('my-reports/<int:report_id>/', views.report_detail_view, name='report_detail'),
]