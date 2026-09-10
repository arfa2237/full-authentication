from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),      
    path('patient/', include('Core.urls')),
    path('staff/', include('Staff.urls')),
    path('tig-secure-dashboard-2026/', include('AdminPanel.urls')),
    path('', include('publicsite.urls')),
]