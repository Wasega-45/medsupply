from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Order, OrderItem, Delivery
from .forms import OrderForm, OrderItemFormSet
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