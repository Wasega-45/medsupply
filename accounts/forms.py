from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from core.models import Facility, SupplyHub


class FacilityRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label="Full Name")
    phone = forms.CharField(max_length=20, required=False)
    facility = forms.ModelChoiceField(
        queryset=Facility.objects.filter(status='active'),
        required=True,
        label="Health Facility",
        empty_label="-- Select your facility --",
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'phone', 'facility')


class HubRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label="Full Name")
    phone = forms.CharField(max_length=20, required=False)
    hub = forms.ModelChoiceField(
        queryset=SupplyHub.objects.filter(active=True),
        required=True,
        label="Supply Hub",
        empty_label="-- Select your supply hub --",
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'phone', 'hub')