from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment_view, name='book_appointment'),
    path('cancel/<int:pk>/', views.cancel_appointment_view, name='cancel_appointment'),
    path('history/', views.appointment_history_view, name='appointment_history'),
    path('confirm/<int:pk>/', views.confirm_appointment_view, name='confirm_appointment'),
    path('complete/<int:pk>/', views.complete_appointment_view, name='complete_appointment'),
    path('symptom-check/', views.symptom_check_view, name='symptom_check'),
    path('toggle-favorite/<int:doctor_id>/', views.toggle_favorite_doctor, name='toggle_favorite'),
    path('get-booked-slots/', views.get_booked_slots, name='get_booked_slots'),
    
]
