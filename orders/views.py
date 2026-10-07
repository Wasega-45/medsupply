from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Order, OrderItem, Delivery
from core.models import Facility, SupplyHub, Inventory


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
    """Return all orders as JSON for the live dashboard."""
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
    """Dashboard shown to facility users after login."""

    # Guard: only facility users should land here
    if request.user.role != 'facility':
        return redirect('post_login_redirect')

    # The user's linked facility
    facility = request.user.facility

    if facility is None:
        # User is a facility user but hasn't been linked to one yet
        return render(request, 'facility/dashboard.html', {
            'facility': None,
            'orders': [],
            'inventory': [],
            'total_orders': 0,
            'pending_orders': 0,
            'delivered_orders': 0,
            'total_stock_items': 0,
        })

    # All orders for this facility, most recent first
    orders = Order.objects.filter(facility=facility).order_by('-requested_at')

    # Inventory for this facility
    inventory = Inventory.objects.filter(facility=facility).select_related('medicine')

    # KPI calculations
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    delivered_orders = orders.filter(status='delivered').count()
    total_stock_items = sum(inv.quantity for inv in inventory)

    context = {
        'facility': facility,
        'orders': orders,
        'inventory': inventory,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'total_stock_items': total_stock_items,
    }
    return render(request, 'facility/dashboard.html', context)