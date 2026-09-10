from django.contrib import admin
from django.urls import path, include
from django.http import Http404
from django.conf import settings

def disabled_admin(request, *args, **kwargs):
    raise Http404

urlpatterns = [
    path('patient/',                    include('Core.urls')),
    path('staff/',                      include('Staff.urls')),
    path('tig-secure-dashboard-2026/', include('AdminPanel.urls')),
    path('',                           include('publicsite.urls')),
]

#  Only enable /admin/ on localhost (DEBUG=True) 
if settings.DEBUG:
    urlpatterns = [path('admin/', admin.site.urls)] + urlpatterns
else:
    urlpatterns = [path('admin/', disabled_admin)] + urlpatterns