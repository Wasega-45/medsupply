from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

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
    facility = models.ForeignKey(
        'core.Facility',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='users',
    )
    hub = models.ForeignKey(
        'core.SupplyHub',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='users',
    )
    
    county = models.ForeignKey('core.County', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"