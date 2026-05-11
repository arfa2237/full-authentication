from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from Core.models import VaccinationCenter


class StaffProfile(models.Model):

    STATUS_CHOICES = [
        ('pending',  'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    ROLE_CHOICES = [
        ('staff', 'Healthcare Staff'),
        ('admin', 'Administrator'),
    ]

    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    center       = models.ForeignKey(VaccinationCenter, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='staff')
    phone        = models.CharField(max_length=15, blank=True, null=True)
    designation  = models.CharField(max_length=100, blank=True, null=True)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    role         = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.status}"

    @property
    def is_approved(self):
        return self.status == 'approved'
   