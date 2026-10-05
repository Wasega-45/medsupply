from django.shortcuts import render
from .models import Order
from core.models import Facility


def order_list(request):
    orders = Order.objects.all().order_by('-requested_at')
    return render(request, 'orders_dashboard.html', {'orders': orders})


def facility_map(request):
    facilities = Facility.objects.all()
    return render(request, 'map.html', {'facilities': facilities})