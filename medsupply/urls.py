from django.contrib import admin
from django.urls import path
from . import views
from orders import views as order_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('orders/', order_views.order_list, name='order_list'),
    path('map/', order_views.facility_map, name='facility_map'),
]