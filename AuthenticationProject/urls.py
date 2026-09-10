from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),   
    path('i18n/', include('django.conf.urls.i18n')),   
    path('patient/', include('Core.urls')),
    path('staff/', include('Staff.urls')),
    path('tig-secure-dashboard-2026/', include('AdminPanel.urls')),
    path('', include('publicsite.urls')),
]