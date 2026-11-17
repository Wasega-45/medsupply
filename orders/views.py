from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
import math
from .models import Order, OrderItem, Delivery
from .forms import OrderForm, OrderItemFormSet
from core.models import Facility, SupplyHub, Inventory, Drone


def order_list(request):
    orders = Order.objects.all().order_by('-requested_at')
    return render(request, 'orders_dashboard.html', {'orders': orders})


def facility_map(request):
    facilities = Facility.objects.all()
    hubs = SupplyHub.objects.filter(active=True)
    return render(request, 'map.html', {
        'facilities': facilities,
        'hubs': hubs,
    })


def delivery_list(request):
    deliveries = Delivery.objects.all().order_by('-created_at')
    return render(request, 'deliveries.html', {'deliveries': deliveries})


def orders_api(request):
    orders = Order.objects.all().order_by('-requested_at')
    data = []
    for o in orders:
        data.append({
            'id': o.id,
            'facility': o.facility.name,
            'priority': o.get_priority_display(),
            'priority_raw': o.priority,
            'status': o.get_status_display(),
            'requested_at': o.requested_at.strftime('%d %b %Y, %H:%M'),
        })
    return JsonResponse({'orders': data, 'count': len(data)})


@login_required
def facility_dashboard(request):
    if request.user.role != 'facility':
        return redirect('post_login_redirect')

    facility = request.user.facility

    if facility is None:
        return render(request, 'facility/dashboard.html', {
            'facility': None,
            'orders': [],
            'inventory': [],
            'total_orders': 0,
            'pending_orders': 0,
            'delivered_orders': 0,
            'total_stock_items': 0,
        })

    orders = Order.objects.filter(facility=facility).order_by('-requested_at')
    inventory = Inventory.objects.filter(facility=facility).select_related('medicine')

    context = {
        'facility': facility,
        'orders': orders,
        'inventory': inventory,
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'delivered_orders': orders.filter(status='delivered').count(),
        'total_stock_items': sum(inv.quantity for inv in inventory),
    }
    return render(request, 'facility/dashboard.html', context)


@login_required
def place_order(request):
    """Facility users submit a new multi-item order."""
    if request.user.role != 'facility':
        return redirect('post_login_redirect')

    facility = request.user.facility
    if facility is None:
        messages.error(request, "Your account is not linked to a facility. Please contact your administrator.")
        return redirect('facility_dashboard')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.facility = facility
            order.requested_by = request.user
            order.status = 'pending'
            order.save()

            formset.instance = order
            formset.save()

            messages.success(request, f"Order #{order.id} submitted successfully.")
            return redirect('facility_dashboard')
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    inventory = Inventory.objects.filter(facility=facility).select_related('medicine')

    context = {
        'facility': facility,
        'form': form,
        'formset': formset,
        'inventory': inventory,
    }
    return render(request, 'facility/place_order.html', context)


# --- LOGISTICS VIEWS ---

@login_required
def logistics_dashboard(request):
    approved_orders = Order.objects.filter(status='approved').order_by('priority', 'requested_at')
    context = {
        'orders': approved_orders,
        'user_hub': request.user.hub
    }
    return render(request, 'logistics/dashboard.html', context)

@login_required
def dispatch_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'approved':
            nearest_hub, distance = order.facility.nearest_hub()
            Delivery.objects.create(
                order=order,
                origin_hub=nearest_hub,
                destination_facility=order.facility,
                method='drone',
                status='pending'
            )
            order.status = 'dispatched'
            order.save()
            
            # Set the drone to in_transit
            drone = Drone.objects.filter(home_hub=nearest_hub, status='idle').first()
            if drone:
                drone.status = 'in_transit'
                drone.save()
                
    return redirect('logistics_dashboard')


# --- DRONE SIMULATION & API ---

def simulate_drones(request):
    """Moves in-transit drones slightly closer to their destination."""
    active_drones = Drone.objects.filter(status='in_transit', active=True)
    
    for drone in active_drones:
        delivery = Delivery.objects.filter(origin_hub=drone.home_hub, status='pending').first()
        
        if delivery:
            delivery.status = 'in_transit'
            delivery.save()
            
            dest_lat = delivery.destination_facility.latitude
            dest_lng = delivery.destination_facility.longitude
            
            if dest_lat and dest_lng and drone.latitude and drone.longitude:
                lat_diff = float(dest_lat) - float(drone.latitude)
                lng_diff = float(dest_lng) - float(drone.longitude)
                distance = math.sqrt(lat_diff**2 + lng_diff**2)
                
                if distance < 0.01:
                    drone.latitude = dest_lat
                    drone.longitude = dest_lng
                    drone.status = 'idle'
                    drone.save()
                    
                    delivery.status = 'delivered'
                    delivery.delivered_at = timezone.now()
                    delivery.save()
                    
                    delivery.order.status = 'delivered'
                    delivery.order.completed_at = timezone.now()
                    delivery.order.save()
                else:
                    # Move 10% closer
                    drone.latitude = float(drone.latitude) + (lat_diff * 0.1)
                    drone.longitude = float(drone.longitude) + (lng_diff * 0.1)
                    drone.save()
                    
    return JsonResponse({'status': 'success'})


def drones_api(request):
    """Returns the current coordinates and status of all active drones."""
    active_drones = Drone.objects.filter(active=True)
    data = []
    for d in active_drones:
        data.append({
            'id': d.id,
            'identifier': d.identifier,
            'lat': d.latitude,
            'lng': d.longitude,
            'status': d.get_status_display(),
        })
    return JsonResponse({'drones': data})