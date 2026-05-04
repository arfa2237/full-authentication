from django.contrib import admin
from .models import Blog, AdminProfile

admin.site.register(Blog)
admin.site.register(AdminProfile)