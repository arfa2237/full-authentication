from django.urls import path
from . import views

urlpatterns = [
    path('login/',                              views.AdminLogin,           name='admin-login'),
    path('logout/',                             views.AdminLogout,          name='admin-logout'),
    path('dashboard/',                          views.AdminDashboard,       name='admin-dashboard'),
    path('staff/',                              views.AdminStaff,           name='admin-staff'),
    path('staff/update/<int:staff_id>/',        views.UpdateStaffStatus,    name='update-staff-status'),
    path('users/',                              views.AdminUsers,           name='admin-users'),
    path('centers/',                            views.AdminCenters,         name='admin-centers'),
    path('appointments/',                       views.AdminAppointments,    name='admin-appointments'),
    path('blogs/',                              views.AdminBlogs,           name='admin-blogs'),
    path('statistics/', views.AdminStatistics, name='admin-statistics'),
]