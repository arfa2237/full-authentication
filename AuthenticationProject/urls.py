from django.contrib import admin
from django.urls import path, include
from django.http import Http404

#  Disable default Django admin 
def disabled_admin(request, *args, **kwargs):
    raise Http404

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', disabled_admin),
    path('patient/', include('Core.urls')),
    path('staff/', include('Staff.urls')),
    path('tig-secure-dashboard-2026/', include('AdminPanel.urls')),
    path('', include('publicsite.urls')),
]