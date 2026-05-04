from django.db import models
from django.contrib.auth.models import User


class Blog(models.Model):
    CATEGORY_CHOICES = [
        ('vaccine',    'Vaccine'),
        ('disease',    'Disease'),
        ('awareness',  'Awareness'),
        ('news',       'News'),
    ]

    title        = models.CharField(max_length=300)
    summary      = models.TextField(max_length=500)
    content      = models.TextField()
    category     = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='awareness')
    author       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class AdminProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin: {self.user.username}"
