from django.urls import path
from . import views

urlpatterns = [
    path('county-approvals/', views.county_admin_approvals, name='county_admin_approvals'),
    path('county-approvals/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('county-approvals/reject/<int:user_id>/', views.reject_user, name='reject_user'),
    path('county-approvals/approve-order/<int:order_id>/', views.approve_order, name='approve_order'),
    path('county-approvals/reject-order/<int:order_id>/', views.reject_order, name='reject_order'),
]