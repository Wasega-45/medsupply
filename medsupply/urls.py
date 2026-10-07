from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from orders import views as order_views
from core import views as core_views
from accounts import views as account_views

admin.site.site_header = "MedSupply Kenya Administration"
admin.site.site_title = "MedSupply Kenya"
admin.site.index_title = "System Administration"

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='auth/logged_out.html'), name='logout'),
    path('post-login/', account_views.post_login_redirect, name='post_login_redirect'),

    # Registration
    path('register/facility/', account_views.register_facility, name='register_facility'),
    path('register/hub/', account_views.register_hub, name='register_hub'),
    path('pending/', account_views.pending_approval, name='pending_approval'),

    # Facility dashboard
    path('dashboard/', order_views.facility_dashboard, name='facility_dashboard'),
    path('order/new/', order_views.place_order, name='place_order'),
    
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),

    # Orders
    path('orders/', order_views.order_list, name='order_list'),
    path('orders/api/', order_views.orders_api, name='orders_api'),

    # Deliveries
    path('deliveries/', order_views.delivery_list, name='delivery_list'),

    # Map & GIS
    path('map/', order_views.facility_map, name='facility_map'),

    # Coverage
    path('coverage/', core_views.coverage_report, name='coverage_report'),
]