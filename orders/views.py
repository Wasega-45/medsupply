from django.shortcuts import render
from .models import Order


def order_list(request):
    orders = Order.objects.all().order_by('-requested_at')
    return render(request, 'orders_dashboard.html', {'orders': orders})