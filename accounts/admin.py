from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'role', 'status', 'county')
    list_filter = ('role', 'status', 'county')
    search_fields = ('username', 'email', 'first_name', 'county__name')

    fieldsets = UserAdmin.fieldsets + (
        ('MedSupply Profile', {
            'fields': ('role', 'status', 'phone', 'facility', 'hub', 'county'),
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('MedSupply Profile', {
            'fields': ('role', 'status', 'phone', 'facility', 'hub', 'county'),
        }),
    )