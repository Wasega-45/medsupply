from django.contrib import admin
from .models import Order, OrderItem, Delivery


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'facility', 'requested_by', 'priority', 'status', 'requested_at')
    list_filter = ('status', 'priority', 'facility')
    search_fields = ('facility__name', 'requested_by__username')
    inlines = [OrderItemInline]


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'origin_hub', 'destination_facility', 'method', 'status', 'created_at')
    list_filter = ('status', 'method', 'origin_hub')
    search_fields = ('order__id', 'destination_facility__name')