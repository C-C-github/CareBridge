from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta  # <--- Added for 4-hour logic
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import random
import json

# Custom Decorators & Utilities
from accounts.decorators import role_required
from accounts.forms import UserProfileForm
from .utils import send_notification

# Import Models & Forms
from appointments.models import Appointment, Doctor
from accounts.models import CustomUser
from records.models import MedicalReport 
from records.forms import MedicalReportForm  # <--- Added Missing Form Import
from .models import Notification

# ==========================================
# 1. PATIENT DASHBOARD (Home)
# ==========================================
@never_cache
@login_required
@role_required(allowed_roles=['patient'])
def patient_dashboard(request):
    # UPDATED: Added 'doctor__user' to select_related to fetch Doctor Names efficiently
    my_appointments = Appointment.objects.filter(patient=request.user)\
                                          .select_related('doctor', 'doctor__user')\
                                          .order_by('-date', '-time')
    
    # Counts
    upcoming_count = my_appointments.filter(status__in=['pending', 'scheduled', 'confirmed']).count()
    completed_count = my_appointments.filter(status='completed').count()
    
    # Reports Count
    report_count = MedicalReport.objects.filter(patient=request.user).count()
    
    # Recent Activity (First 5)
    recent_activity = my_appointments[:5]

    # Recent Notifications (For Dashboard Widget)
    recent_notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:3]

    context = {
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'report_count': report_count,
        'recent_activity': recent_activity,
        'recent_notifications': recent_notifications, 
    }
    return render(request, 'dashboard/patient_home.html', context)


# ==========================================
# 2. PATIENT: UPCOMING APPOINTMENTS
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def patient_upcoming(request):
    """
    Shows pending and confirmed appointments.
    """
    appointments = Appointment.objects.filter(
        patient=request.user, 
        status__in=['pending', 'confirmed', 'scheduled']
    ).select_related('doctor', 'doctor__user').order_by('date', 'time')
    
    return render(request, 'dashboard/patient_upcoming.html', {'appointments': appointments})


# ==========================================
# 3. PATIENT: HISTORY (COMPLETED)
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def patient_history(request):
    """
    Shows completed appointments with links to medical reports.
    """
    appointments = Appointment.objects.filter(
        patient=request.user, 
        status='completed'
    ).select_related('doctor', 'doctor__user').order_by('-date', '-time')
    
    return render(request, 'dashboard/patient_history.html', {'appointments': appointments})


# ==========================================
# 4. DOCTOR DASHBOARD (Updated with Report Access Logic)
# ==========================================
@never_cache
@login_required
@role_required(allowed_roles=['doctor'])
def doctor_dashboard(request):
    # 1. AUTO-SYNC: Ensure the user has a linked Doctor Profile
    doctor_profile, created = Doctor.objects.get_or_create(user=request.user)
    if created:
        print(f"Auto-created Doctor Profile for {request.user.username}")

    today = timezone.now().date()
    now = timezone.now()

    # 2. PENDING REQUESTS (For the "Requests" Card)
    pending_appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        status='pending'
    ).select_related('patient').order_by('date', 'time')

    # 3. TODAY'S SCHEDULE (Includes Logic for Report Access)
    todays_appointments = Appointment.objects.filter(
        doctor=doctor_profile, 
        date=today
    ).select_related('patient').order_by('time')
    
    # --- 4-HOUR ACCESS LOGIC START ---
    for appointment in todays_appointments:
        # Create full datetime object for the appointment start
        appt_start_time = timezone.make_aware(
            datetime.combine(appointment.date, appointment.time)
        )
        
        # Calculate Deadline: Appointment Time + 4 Hours
        access_deadline = appt_start_time + timedelta(hours=4)

        # ACCESS RULE:
        # 1. MUST be Confirmed (or Completed)
        # 2. Current time MUST be before the deadline (Start + 4 hrs)
        if appointment.status in ['confirmed', 'completed'] and now <= access_deadline:
            # Access Granted: Fetch previous reports excluding current one
            previous_reports = MedicalReport.objects.filter(
                patient=appointment.patient
            ).exclude(
                appointment=appointment
            ).order_by('-created_at')
            
            appointment.previous_reports = previous_reports
            appointment.can_view_reports = True
        else:
            # Access Denied
            appointment.previous_reports = None
            appointment.can_view_reports = False
    # --- 4-HOUR ACCESS LOGIC END ---

    # 4. Calculate Stats
    total_patients_count = Appointment.objects.filter(doctor=doctor_profile).values('patient').distinct().count()
    pending_count = pending_appointments.count()
    completed_today = todays_appointments.filter(status='completed').count()
    
    # 5. Upcoming appointments (Future dates)
    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        date__gt=today 
    ).select_related('patient').order_by('date', 'time')
    
    total_count = Appointment.objects.filter(doctor=doctor_profile).count()

    # Recent Notifications
    recent_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]

    context = {
        'doctor': doctor_profile,
        'pending_appointments': pending_appointments, 
        'todays_appointments': todays_appointments, # Now carries report access data
        'appointments': upcoming_appointments, 
        'total_patients_count': total_patients_count,
        'pending_count': pending_count, 
        'completed_today': completed_today,
        'today_count': todays_appointments.count(),
        'total_count': total_count,
        'notifications': recent_notifications 
    }
    return render(request, 'dashboard/doctor_home.html', context)


# ==========================================
# 5. ADMIN DASHBOARD
# ==========================================
@never_cache
@login_required
@role_required(allowed_roles=['admin'])
def admin_dashboard(request):
    total_patients = CustomUser.objects.filter(role='patient').count()
    total_doctors = CustomUser.objects.filter(role='doctor').count()
    total_appointments = Appointment.objects.count()
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
    }
    return render(request, 'dashboard/admin_home.html', context)


# ==========================================
# 6. DOCTOR'S PATIENT DIRECTORY
# ==========================================
@login_required
@role_required(allowed_roles=['doctor'])
def doctor_patient_list(request):
    doctor_profile, _ = Doctor.objects.get_or_create(user=request.user)

    patient_ids = Appointment.objects.filter(doctor=doctor_profile).values_list('patient_id', flat=True).distinct()
    patients = CustomUser.objects.filter(id__in=patient_ids)
    today = timezone.now().date()

    for patient in patients:
        upcoming_appt = Appointment.objects.filter(
            patient=patient, 
            doctor=doctor_profile, 
            date__gte=today
        ).order_by('date', 'time').first()

        if upcoming_appt:
            patient.display_appt = upcoming_appt
            if upcoming_appt.date == today:
                patient.appt_status = 'Today'
                patient.status_color = 'warning'
            else:
                patient.appt_status = 'Upcoming'
                patient.status_color = 'primary'
        else:
            last_appt = Appointment.objects.filter(
                patient=patient, 
                doctor=doctor_profile, 
                date__lt=today
            ).order_by('-date', '-time').first()
            
            patient.display_appt = last_appt
            patient.appt_status = 'Last Visit'
            patient.status_color = 'secondary'

    return render(request, 'dashboard/doctor_patients.html', {'patients': patients})


# ==========================================
# 7. COMPLETE APPOINTMENT (Doctor Action)
# ==========================================
@login_required
@role_required(allowed_roles=['doctor'])
def complete_appointment(request, appointment_id):
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor_profile)
    
    # 1. Update Status & Timestamp
    appointment.status = 'completed'
    appointment.completed_at = timezone.now()
    appointment.save()
    
    messages.success(request, "Appointment finished. Please write the medical report.")
    
    send_notification(
        user=appointment.patient,
        message=f"Your visit with Dr. {request.user.last_name} is complete. Report pending.",
        category='report'
    )
    
    # 2. Redirect to Report Creation Page
    return redirect('doctor_upload_report', appointment_id=appointment.id)


# ==========================================
# 8. JOIN MEETING (Auto-Complete Logic)
# ==========================================
@login_required
def join_meeting(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # If DOCTOR joins -> Mark Complete & Notify Patient
    if hasattr(request.user, 'doctor_profile') and appointment.doctor.user == request.user:
        if appointment.status != 'completed':
            appointment.status = 'completed'
            appointment.completed_at = timezone.now()
            appointment.save()
            messages.success(request, "Meeting started. Appointment marked as Completed.")
            
            # Notify Patient that doctor is waiting
            send_notification(
                user=appointment.patient,
                message=f"Dr. {request.user.last_name} has started the video call. Click to join!",
                category='appointment',
                link=appointment.meeting_link
            )
    
    if appointment.meeting_link:
        return redirect(appointment.meeting_link)
    else:
        messages.error(request, "Meeting link not found.")
        return redirect('doctor_dashboard')


# ==========================================
# 9. CONFIRM APPOINTMENT (Doctor Action)
# ==========================================
@login_required
@role_required(allowed_roles=['doctor'])
def confirm_appointment(request, appointment_id):
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor_profile)
    
    if appointment.status == 'pending':
        appointment.status = 'confirmed'
        appointment.save()
        messages.success(request, f"Appointment confirmed.")
        
        # Notify Patient
        send_notification(
            user=appointment.patient,
            message=f"Dr. {request.user.last_name} confirmed your appointment for {appointment.date}.",
            category='appointment',
            link='/dashboard/patient/upcoming/'
        )
    
    return redirect('doctor_dashboard')


# ==========================================
# 10. DOCTOR CANCEL APPOINTMENT
# ==========================================
@login_required
@role_required(allowed_roles=['doctor'])
def doctor_cancel_appointment(request, appointment_id):
    doctor_profile = get_object_or_404(Doctor, user=request.user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor_profile)
    
    appointment.status = 'cancelled'
    appointment.save()
    messages.warning(request, "Appointment has been cancelled.")
    
    # Notify Patient
    send_notification(
        user=appointment.patient,
        message=f"Dr. {request.user.last_name} has cancelled your appointment.",
        category='system',
        link='/dashboard/patient-dashboard/'
    )
    
    return redirect('doctor_dashboard')


# ==========================================
# 11. PATIENT CANCEL APPOINTMENT
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if appointment.status != 'completed':
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
        
        # Notify Doctor
        send_notification(
            user=appointment.doctor.user,
            message=f"Patient {request.user.username} cancelled their appointment.",
            category='appointment',
            link='/dashboard/doctor-dashboard/'
        )
    else:
        messages.error(request, "Cannot cancel a completed appointment.")
        
    return redirect('patient_dashboard')


# ==========================================
# 12. REPORT ISSUE (Patient Flags Missed Appt)
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def report_appointment_issue(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    # Check if we can report (using the property we added to the Model)
    if hasattr(appointment, 'can_report_issue') and appointment.can_report_issue:
        appointment.status = 'doctor_missed'
        appointment.save()
        
        # Notify Support/System
        send_notification(
            user=request.user,
            message=f"We received your report for the appointment with Dr. {appointment.doctor.user.last_name}. Support will review this shortly.",
            category='support'
        )
        
        messages.success(request, "Issue reported. We apologize for the inconvenience.")
    else:
        messages.error(request, "You cannot report this appointment yet. Please wait 15 minutes after the start time.")
    
    return redirect('patient_dashboard')


# ==========================================
# 13. SEND STATUS (Late/Ready/Reschedule)
# ==========================================
@login_required
@require_POST
def send_appointment_status(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    status_type = request.POST.get('status_type')
    
    messages_map = {
        'late_5': f"Patient {request.user.first_name} is running 5 minutes late for your appointment.",
        'late_10': f"Patient {request.user.first_name} is running 10 minutes late.",
        'ready': f"Patient {request.user.first_name} is ready and waiting in the lobby.",
        'cant_make': f"Patient {request.user.first_name} cannot make it and requests a reschedule."
    }
    
    message = messages_map.get(status_type)
    
    if message:
        send_notification(
            user=appointment.doctor.user,
            message=message,
            category='appointment',
            link=f"/dashboard/doctor-dashboard/" 
        )
        messages.success(request, "Status update sent to the doctor.")
    else:
        messages.error(request, "Invalid status update.")
        
    return redirect('patient_dashboard')


# ==========================================
# 14. VIEW ALL APPOINTMENTS (Legacy List)
# ==========================================
@login_required
@role_required(allowed_roles=['patient'])
def appointment_list(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date', '-time')
    return render(request, 'dashboard/appointment_list.html', {'appointments': appointments})


# ==========================================
# 15. PROFILE SETTINGS
# ==========================================
@never_cache
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile details updated successfully.")
            
            send_notification(
                user=request.user,
                message="Security Alert: Your profile details were updated.",
                category='profile',
                link='/dashboard/profile/'
            )
            
            if request.user.role == 'doctor':
                return redirect('doctor_dashboard')
            else:
                return redirect('patient_dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'dashboard/profile.html', {'form': form})


# ==========================================
# 16. NOTIFICATIONS (Dedicated Page)
# ==========================================
@never_cache
@login_required
def notifications_page(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'dashboard/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    
    if notification.link:
        return redirect(notification.link)
    
    return redirect('notifications_page')

@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('notifications_page')

@login_required
def clear_all_notifications(request):
    Notification.objects.filter(recipient=request.user).delete()
    messages.success(request, "All notifications cleared.")
    return redirect('notifications_page')

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.delete()
    messages.success(request, "Notification removed.")
    return redirect('notifications_page')


# ==========================================
# 17. AJAX: SECURITY OTP
# ==========================================
def send_security_otp(request):
    if request.method == "POST" and request.user.is_authenticated:
        otp = str(random.randint(100000, 999999))
        request.session['security_otp'] = otp
        request.session.set_expiry(300) 

        subject = "Security Verification Code - CareBridge"
        message = f"Your OTP for password change is: {otp}\n\nDo not share this code."
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])
            return JsonResponse({'status': 'success', 'message': 'OTP sent to your email.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Failed to send email.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def verify_security_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_otp = data.get('otp')
        session_otp = request.session.get('security_otp')

        if session_otp and user_otp == session_otp:
            del request.session['security_otp']
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid or expired OTP.'})
    return JsonResponse({'status': 'error'})


def services(request):
    return render(request, 'services.html')


# ==========================================
# 18. REPORT MANAGEMENT (UPLOAD & EDIT) - ADDED
# ==========================================
@login_required
@role_required(allowed_roles=['doctor'])
def doctor_upload_report_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Security Check: Ensure this appointment belongs to the logged-in doctor
    if appointment.doctor.user != request.user:
        messages.error(request, "You are not authorized to view this appointment.")
        return redirect('doctor_dashboard')

    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.patient = appointment.patient
            report.doctor = appointment.doctor
            report.appointment = appointment
            report.save()
            
            # Auto-mark appointment as completed
            appointment.status = 'completed'
            appointment.save()
            
            messages.success(request, "Medical Report created successfully!")
            return redirect('doctor_dashboard')
    else:
        form = MedicalReportForm()

    context = {
        'form': form,
        'appointment': appointment,
        'patient': appointment.patient
    }
    return render(request, 'dashboard/doctor_upload_report.html', context)

@login_required
@role_required(allowed_roles=['doctor'])
def doctor_edit_report_view(request, report_id):
    report = get_object_or_404(MedicalReport, id=report_id)
    
    if request.method == 'POST':
        form = MedicalReportForm(request.POST, request.FILES, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, "Report updated successfully.")
            return redirect('doctor_dashboard')
    else:
        form = MedicalReportForm(instance=report)

    return render(request, 'dashboard/doctor_upload_report.html', {
        'form': form,
        'appointment': report.appointment,
        'patient': report.patient,
        'is_edit': True
    })
    