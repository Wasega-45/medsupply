from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import County, Facility
from orders.models import Order

User = get_user_model()

class AdminApprovalTest(TestCase):
    def setUp(self):
        # 1. Create a County
        self.county = County.objects.create(name="Kisumu", code="KSI")
        
        # 2. Create a Facility
        self.facility = Facility.objects.create(
            name="Kisumu Clinic",
            county=self.county,
            facility_type="clinic"
        )
        
        # 3. Create a County Admin
        self.admin_user = User.objects.create_user(
            username="countyadmin",
            password="adminpassword123",
            role="county_admin",
            status="active",
            county=self.county
        )
        
        # 4. Create a Pending Order
        self.order = Order.objects.create(
            facility=self.facility,
            status="pending",
            priority="urgent"
        )

    def test_approve_order(self):
        """Test that a County Admin can log in and approve an order."""
        # Log in the admin
        self.client.login(username="countyadmin", password="adminpassword123")
        
        # Submit the approval POST request
        response = self.client.post(reverse('approve_order', args=[self.order.id]))
        
        # Check that it redirected back to the approvals page
        self.assertEqual(response.status_code, 302)
        
        # Refresh the order from the database
        self.order.refresh_from_db()
        
        # Check that the status changed to 'approved'
        self.assertEqual(self.order.status, 'approved')
        self.assertIsNotNone(self.order.approved_at)