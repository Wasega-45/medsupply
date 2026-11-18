from django.urls import path
from . import views

urlpatterns = [
    path('', views.logistics_dashboard, name='logistics_dashboard'),
    path('dispatch/<int:order_id>/', views.dispatch_order, name='dispatch_order'),
    path('inventory/', views.hub_inventory, name='hub_inventory'),
    path('inventory/update/', views.update_inventory, name='update_inventory'),
    path('api/simulate-drones/', views.simulate_drones, name='simulate_drones'),
    path('api/drones/', views.drones_api, name='drones_api'),
]