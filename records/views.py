from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import doctor_only, patient_only
from .forms import MedicalReportForm
from appointments.models import Doctor, Appointment
from .models import MedicalReport

# ==========================================
#               DOCTOR VIEWS
# ==========================================

@login_required
@doctor_only
def upload_report_view(request, appointment_id):
    """
    Doctor uploads a report for a specific appointment.
    Links the report to the appointment, patient, and doctor.
    """
    # Ensure the appointment belongs to the logged-in doctor
    doctor_profile = request.user.doctor_profile
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor_profile)

    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.doctor = doctor_profile
            report.patient = appointment.patient
            report.appointment = appointment
            report.save()
            messages.success(request, "Medical report uploaded successfully!")
            return redirect('doctor_dashboard')
    else:
        form = MedicalReportForm()

    return render(request, 'records/upload_report.html', {'form': form, 'appointment': appointment})


@login_required
@doctor_only
def edit_report_view(request, report_id):
    """
    Doctor edits an existing medical report.
    """
    # Ensure the report belongs to the logged-in doctor
    doctor_profile = request.user.doctor_profile
    report = get_object_or_404(MedicalReport, id=report_id, doctor=doctor_profile)

    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, "Medical report updated successfully.")
            return redirect('doctor_dashboard')
    else:
        form = MedicalReportForm(instance=report)

    # Reuse the same template; pass appointment if present for header context
    return render(request, 'records/upload_report.html', {
        'form': form,
        'appointment': report.appointment if hasattr(report, 'appointment') else None,
    })


# ==========================================
#               PATIENT VIEWS
# ==========================================

@login_required
@patient_only
def patient_reports_view(request):
    # Fetch all reports for the logged-in user
    reports = MedicalReport.objects.filter(patient=request.user).order_by('-created_at')
    return render(request, 'records/patient_reports.html', {'reports': reports})

@login_required
@patient_only
def report_detail_view(request, report_id):
    """
    Show full details for a single report, ensuring it belongs to the logged-in patient.
    """
    report = get_object_or_404(MedicalReport, id=report_id, patient=request.user)
    return render(request, 'records/report_detail.html', {'report': report})