from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('register/', views.RegisterView, name='register'), 
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
    path('book-appointment/', views.BookAppointment, name='book-appointment'),
    path('my-appointments/', views.MyAppointments, name='my-appointments'),
    path('cancel-appointment/<int:appt_id>/', views.CancelAppointment, name='cancel-appointment'),
    path('vaccine-card/', views.VaccineCard, name='vaccine-card'),
    path('download-vaccine-card/', views.DownloadVaccineCard, name='download-vaccine-card'),
    path('my-records/', views.MyRecords, name='my-records'),
]
