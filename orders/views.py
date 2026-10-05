from django.shortcuts import render
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