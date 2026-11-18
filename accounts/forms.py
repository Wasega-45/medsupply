from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from core.models import Facility, SupplyHub, County


class FacilityRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label="Full Name")
    phone = forms.CharField(max_length=20, required=False)
    
    facility_name = forms.CharField(max_length=150, required=True, label="Facility Name")
    county = forms.ModelChoiceField(queryset=County.objects.all(), required=True, label="County")
    facility_type = forms.ChoiceField(choices=Facility.FACILITY_TYPES, required=True, label="Facility Type")
    location = forms.CharField(max_length=255, required=True, label="Physical Address / Town Name")
    
    latitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        
        facility = Facility.objects.create(
            name=self.cleaned_data['facility_name'],
            county=self.cleaned_data['county'],
            facility_type=self.cleaned_data['facility_type'],
            location=self.cleaned_data['location'],
            latitude=self.cleaned_data.get('latitude'),
            longitude=self.cleaned_data.get('longitude'),
            status='inactive'
        )
        
        user.facility = facility
        user.county = self.cleaned_data['county']
        if commit:
            user.save()
        return user


class HubRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label="Full Name")
    phone = forms.CharField(max_length=20, required=False)
    
    hub_name = forms.CharField(max_length=150, required=True, label="Hub Name")
    county = forms.ModelChoiceField(queryset=County.objects.all(), required=True, label="County")
    location = forms.CharField(max_length=255, required=True, label="Physical Address / Town Name")
    service_radius_km = forms.IntegerField(required=True, initial=50, label="Service Radius (km)")
    
    latitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)
    longitude = forms.DecimalField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        
        hub = SupplyHub.objects.create(
            name=self.cleaned_data['hub_name'],
            county=self.cleaned_data['county'],
            location=self.cleaned_data['location'],
            latitude=self.cleaned_data.get('latitude'),
            longitude=self.cleaned_data.get('longitude'),
            service_radius_km=self.cleaned_data['service_radius_km'],
            active=False
        )
        
        user.hub = hub
        user.county = self.cleaned_data['county']
        if commit:
            user.save()
        return user