from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'facility', 'requested_by', 'priority', 'status', 'requested_at')
    list_filter = ('status', 'priority', 'facility')
    search_fields = ('facility__name', 'requested_by__username')
    inlines = [OrderItemInline]