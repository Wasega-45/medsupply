from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'role', 'status', 'is_superuser')
    list_filter = ('role', 'status', 'is_superuser', 'is_staff')
    search_fields = ('username', 'email', 'first_name')

    fieldsets = UserAdmin.fieldsets + (
        ('MedSupply Profile', {
            'fields': ('role', 'status', 'phone', 'facility', 'hub'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('MedSupply Profile', {
            'fields': ('role', 'status', 'phone', 'facility', 'hub'),
        }),
    )