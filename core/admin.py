from django.contrib import admin
from .models import County, Facility, Medicine, Inventory


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