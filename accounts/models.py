from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('facility', 'Health Facility User'),
        ('logistics', 'Supply/Logistics Officer'),
        ('county_admin', 'County Administrator'),
        ('national_admin', 'National/System Administrator'),
        ('monitoring', 'Monitoring/Operations User'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Approval'),
        ('suspended', 'Suspended'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='facility')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"