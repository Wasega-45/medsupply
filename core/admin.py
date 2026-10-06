from django.contrib import admin
from .models import County, Facility, Medicine, Inventory, SupplyHub, Drone


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'facility_type', 'county', 'status')
    list_filter = ('facility_type', 'county', 'status')
    search_fields = ('name', 'contact')


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'reorder_level', 'active')
    list_filter = ('category', 'active')
    search_fields = ('name', 'category')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('facility', 'medicine', 'quantity', 'reserved_quantity', 'updated_at')
    list_filter = ('facility', 'medicine')
    search_fields = ('facility__name', 'medicine__name')


@admin.register(SupplyHub)
class SupplyHubAdmin(admin.ModelAdmin):
    list_display = ('name', 'county', 'service_radius_km', 'active')
    list_filter = ('county', 'active')
    search_fields = ('name', 'location')


@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'operator', 'status', 'home_hub', 'active', 'last_update')
    list_filter = ('status', 'active', 'home_hub')
    search_fields = ('identifier', 'operator')