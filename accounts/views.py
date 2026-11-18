from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .forms import FacilityRegistrationForm, HubRegistrationForm
from .models import User


def register_facility(request):
    if request.method == 'POST':
        form = FacilityRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            lat = form.cleaned_data.get('latitude')
            lng = form.cleaned_data.get('longitude')
            
            if not lat or not lng:
                lat, lng = -0.0236, 37.9062

            user.facility.latitude = lat
            user.facility.longitude = lng
            user.facility.save()
                
            user.role = 'facility'
            user.status = 'pending'
            user.save()
            
            messages.success(request, "Registration submitted! Your facility is pending approval.")
            return redirect('pending_approval')
    else:
        form = FacilityRegistrationForm()

    return render(request, 'auth/register_facility.html', {'form': form})


def register_hub(request):
    if request.method == 'POST':
        form = HubRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            lat = form.cleaned_data.get('latitude')
            lng = form.cleaned_data.get('longitude')
            
            if not lat or not lng:
                lat, lng = -0.0236, 37.9062

            user.hub.latitude = lat
            user.hub.longitude = lng
            user.hub.save()
            
            user.role = 'logistics'
            user.status = 'pending'
            user.save()
            
            messages.success(request, "Registration submitted! Your hub is pending approval.")
            return redirect('pending_approval')
    else:
        form = HubRegistrationForm()

    return render(request, 'auth/register_hub.html', {'form': form})


def pending_approval(request):
    return render(request, 'auth/pending.html')


@login_required
def post_login_redirect(request):
    user = request.user

    if user.status != 'active' and not user.is_superuser:
        return redirect('pending_approval')

    if user.role == 'county_admin':
        return redirect('county_admin_approvals')
    elif user.is_superuser or user.role == 'national_admin':
        return redirect('/admin/')
    elif user.role == 'logistics':
        return redirect('logistics_dashboard')
    elif user.role == 'facility':
        return redirect('facility_dashboard')
    elif user.role == 'monitoring':
        return redirect('order_list')
    else:
        return redirect('/admin/')


# --- COUNTY ADMIN APPROVAL VIEWS ---

@login_required
def county_admin_approvals(request):
    from orders.models import Order
    
    admin_county = request.user.county 
    
    # SECURITY CHECK: If they don't have a county assigned, block them!
    if not admin_county:
        messages.error(request, "Your account is not assigned to a county. Please contact the National Admin.")
        return redirect('home')

    # Filter users where EITHER the user's county OR their facility/hub county matches the admin's county
    pending_users = User.objects.filter(
        Q(county=admin_county) | Q(facility__county=admin_county) | Q(hub__county=admin_county),
        status='pending'
    ).select_related('facility', 'hub').distinct()

    # Filter orders strictly by the admin's county
    pending_orders = Order.objects.filter(
        status='pending',
        facility__county=admin_county
    ).select_related('facility').prefetch_related('items__medicine')

    return render(request, 'auth/county_approvals.html', {
        'pending_users': pending_users,
        'pending_orders': pending_orders,
        'county': admin_county
    })

@login_required
def approve_user(request, user_id):
    if request.method == 'POST':
        user_to_approve = get_object_or_404(User, id=user_id)
        
        # Security check: Ensure they are in the same county
        is_same_county = (
            user_to_approve.county == request.user.county or 
            (user_to_approve.facility and user_to_approve.facility.county == request.user.county) or
            (user_to_approve.hub and user_to_approve.hub.county == request.user.county)
        )

        if is_same_county:
            user_to_approve.status = 'active' 
            user_to_approve.save()
            
            if user_to_approve.facility:
                user_to_approve.facility.status = 'active'
                user_to_approve.facility.save()
            if user_to_approve.hub:
                user_to_approve.hub.active = True
                user_to_approve.hub.save()
                
            messages.success(request, f"Approved {user_to_approve.username}")
        else:
            messages.error(request, "You cannot approve a user outside your county.")
            
    return redirect('county_admin_approvals')

@login_required
def reject_user(request, user_id):
    if request.method == 'POST':
        user_to_reject = get_object_or_404(User, id=user_id)
        
        is_same_county = (
            user_to_reject.county == request.user.county or 
            (user_to_reject.facility and user_to_reject.facility.county == request.user.county) or
            (user_to_reject.hub and user_to_reject.hub.county == request.user.county)
        )

        if is_same_county:
            user_to_reject.status = 'rejected' 
            user_to_reject.save()
            messages.warning(request, f"Rejected {user_to_reject.username}")
        else:
            messages.error(request, "You cannot reject a user outside your county.")
            
    return redirect('county_admin_approvals')

@login_required
def approve_order(request, order_id):
    from orders.models import Order
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        
        if order.facility.county == request.user.county:
            order.status = 'approved'
            order.approved_at = timezone.now()
            order.save()
            messages.success(request, f"Approved Order #{order.id}")
        else:
            messages.error(request, "You cannot approve an order outside your county.")
            
    return redirect('county_admin_approvals')

@login_required
def reject_order(request, order_id):
    from orders.models import Order
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        
        if order.facility.county == request.user.county:
            order.status = 'rejected'
            order.save()
            messages.warning(request, f"Rejected Order #{order.id}")
        else:
            messages.error(request, "You cannot reject an order outside your county.")
            
    return redirect('county_admin_approvals')