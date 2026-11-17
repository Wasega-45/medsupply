from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from core.models import County, Facility, Medicine, Inventory
from orders.models import Order, OrderItem

User = get_user_model()

class OrderFlowTest(TestCase):
    def setUp(self):
        # 1. Create a County
        self.county = County.objects.create(name="Test County", code="TC")
        
        # 2. Create a Facility
        self.facility = Facility.objects.create(
            name="Test Facility",
            county=self.county,
            facility_type="clinic",
            latitude=-1.2921,
            longitude=36.8219
        )
        
        # 3. Create a Facility User
        self.facility_user = User.objects.create_user(
            username="testfacility",
            password="testpassword123",
            role="facility",
            status="active",
            facility=self.facility,
            county=self.county
        )
        
        # 4. Create a Medicine
        self.medicine = Medicine.objects.create(name="Paracetamol", unit="tablets")
        
        # 5. Add inventory for the facility
        Inventory.objects.create(facility=self.facility, medicine=self.medicine, quantity=100)

    def test_place_order(self):
        """Test that a facility user can log in and place an order."""
        # Log in the user
        self.client.login(username="testfacility", password="testpassword123")
        
        # Submit the order form
        response = self.client.post(reverse('place_order'), {
            'priority': 'normal',
            'notes': 'Urgent need for paracetamol',
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-medicine': self.medicine.id,
            'items-0-quantity': '10',
        })
        
        # Check that the order was created
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.facility, self.facility)
        
        # Check that the order item was created
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().medicine, self.medicine)
        self.assertEqual(order.items.first().quantity, 10)