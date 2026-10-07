from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import FacilityRegistrationForm, HubRegistrationForm


def register_facility(request):
    if request.method == 'POST':
        form = FacilityRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'facility'
            user.status = 'pending'
            user.facility = form.cleaned_data['facility']
            user.save()
            return redirect('pending_approval')
    else:
        form = FacilityRegistrationForm()

    return render(request, 'auth/register_facility.html', {'form': form})


def register_hub(request):
    if request.method == 'POST':
        form = HubRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'logistics'
            user.status = 'pending'
            user.hub = form.cleaned_data['hub']
            user.save()
            return redirect('pending_approval')
    else:
        form = HubRegistrationForm()

    return render(request, 'auth/register_hub.html', {'form': form})


def pending_approval(request):
    return render(request, 'auth/pending.html')


@login_required
def post_login_redirect(request):
    """Redirect users to the right page based on their role."""
    user = request.user

    # Block if status isn't active
    if user.status != 'active' and not user.is_superuser:
        return redirect('pending_approval')

    if user.is_superuser or user.role == 'national_admin':
        return redirect('/admin/')
    elif user.role == 'county_admin':
        return redirect('/admin/')
    elif user.role == 'logistics':
        return redirect('/admin/')
    elif user.role == 'facility':
        return redirect('facility_dashboard')
    elif user.role == 'monitoring':
        return redirect('order_list')
    else:
        return redirect('/admin/')