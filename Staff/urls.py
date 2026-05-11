from django.urls import path, include
from . import views

urlpatterns = [
    path('signup/',                                  views.StaffSignup,              name='staff-signup'),
    path('login/',                                   views.StaffLogin,               name='staff-login'),
    path('logout/',                                  views.StaffLogout,              name='staff-logout'),
    path('dashboard/',                               views.StaffDashboard,           name='staff-dashboard'),
    path('appointments/',                            views.StaffAppointments,        name='staff-appointments'),
    path('appointments/update/<int:appt_id>/',       views.UpdateAppointmentStatus,  name='update-appointment-status'),
    path('patients/',                                views.StaffPatients,            name='staff-patients'),
]