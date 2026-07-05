from django.db import models
from django.contrib.auth.models import User
import uuid

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"
    
class PatientProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    unique_pin = models.CharField(max_length=20, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.unique_pin:
            number = str(uuid.uuid4().int)[:4]
            self.unique_pin = f"TIG-{number}-GRW"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} — {self.unique_pin}"
    

    
# NEW: Vaccination Center

class VaccinationCenter(models.Model):
    name         = models.CharField(max_length=200)
    address      = models.CharField(max_length=300)
    latitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True) #North or South
    longitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True) #East or West
    availability = models.CharField(max_length=100, default="Open 10am–2pm")
    is_active    = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
# NEW: Appointment 

class Appointment(models.Model):

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('missed',    'Missed'),
        ('cancelled', 'Cancelled'),
    ]
    GENDER_CHOICES = [
        ('male',   'Male (Boy)'),
        ('female', 'Female (Girl)'),
    ]

    VACCINE_CHOICES = [
        ('Child Vaccine - At Birth',       'Child Vaccine - At Birth'),
        ('Child Vaccine - 6 week',               'Child Vaccine - 6 week'),
        ('Child Vaccine - 10 week',           'Child Vaccine - 10 week'),
        ('Child Vaccine - 14 week',      'Child Vaccine - 14 week'),
        ('Child Vaccine - 9 months', 'Child Vaccine - 9 months'),
        ('Child Vaccine - 15 months',          'Child Vaccine - 15 months'),
    ]

    patient          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    center           = models.ForeignKey(VaccinationCenter, on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='appointments')
    vaccine_type     = models.CharField(max_length=100, choices=VACCINE_CHOICES)
    dose_number      = models.PositiveSmallIntegerField(default=1)   
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    notes            = models.TextField(blank=True, null=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at       = models.DateTimeField(auto_now_add=True)
    # Child/Patient Information
    child_name       = models.CharField(max_length=100, blank=True, null=True)
    child_gender     = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    guardian_name    = models.CharField(max_length=100, blank=True, null=True)
    guardian_cnic    = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.child_name or self.patient.username} — {self.vaccine_type}"

    class Meta:
        ordering = ['appointment_date', 'appointment_time']

    def __str__(self):
        return f"{self.patient.username} — {self.vaccine_type} Dose {self.dose_number} on {self.appointment_date}"