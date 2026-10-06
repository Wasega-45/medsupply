from django.contrib import admin
from django.urls import path
from . import views
from orders import views as order_views
from core import views as core_views

admin.site.site_header = "MedSupply Kenya Administration"
admin.site.site_title = "MedSupply Kenya"
admin.site.index_title = "System Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('orders/', order_views.order_list, name='order_list'),
    path('orders/api/', order_views.orders_api, name='orders_api'),
    path('map/', order_views.facility_map, name='facility_map'),
    path('deliveries/', order_views.delivery_list, name='delivery_list'),
    path('coverage/', core_views.coverage_report, name='coverage_report'),
]