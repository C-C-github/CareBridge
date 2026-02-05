from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # ==========================================
    # 1. LANDING PAGE
    # ==========================================
    path('', views.home_view, name='home'),

    # ==========================================
    # 2. LOGIN PATHS (CRITICAL FIX ADDED)
    # ==========================================
    # This acts as a "catch-all" for the default login redirect.
    # It points to your Patient Login view so users never see a 404/Template Error.
    path('login/', views.patient_login_view, name='login'),

    path('login/patient/', views.patient_login_view, name='patient_login'),
    path('login/staff/', views.staff_login_view, name='staff_login'),

    # ==========================================
    # 3. AUTH PATHS
    # ==========================================
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # ==========================================
    # 4. OTP PATHS (General)
    # ==========================================
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),

    # ==========================================
    # 5. PROFILE PATHS
    # ==========================================
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),

    # ==========================================
    # 6. PATIENT PASSWORD RESET (Existing / Green Theme)
    # ==========================================
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), 
         name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), 
         name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),

    # ==========================================
    # 7. STAFF PASSWORD RESET (Custom OTP Flow)
    # ==========================================
    # Step 1: Enter Staff ID
    path('login/staff/password-reset/', views.staff_password_reset, name='staff_password_reset'),
    
    # Step 2: Enter OTP Code
    path('login/staff/password-reset/verify/', views.staff_password_reset_verify, name='staff_password_reset_verify'),
    
    # Step 3: Set New Password
    path('login/staff/password-reset/confirm/', views.staff_password_reset_confirm, name='staff_password_reset_confirm'),
    path('admin/upload-doctors/', views.bulk_upload_doctors_view, name='bulk_upload_doctors'),
]