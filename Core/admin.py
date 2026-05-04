from django.contrib import admin
from .models import PasswordReset, PatientProfile, VaccinationCenter, Appointment

admin.site.register(PasswordReset)
admin.site.register(PatientProfile)
admin.site.register(VaccinationCenter)
admin.site.register(Appointment)
