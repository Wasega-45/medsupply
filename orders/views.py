from django.shortcuts import render
from django.http import JsonResponse
from .models import Order, Delivery
from core.models import Facility, SupplyHub


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