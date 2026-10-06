from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

from .models import Order, OrderItem, Delivery
from core.models import County, Facility, Medicine, SupplyHub


User = get_user_model()


class OrderModelTest(TestCase):
    """Database tests for Order and OrderItem."""

    def setUp(self):
        self.county = County.objects.create(name="Kisumu", code="KSM")
        self.facility = Facility.objects.create(name="Test Facility", county=self.county)
        self.user = User.objects.create_user(username="testuser", password="pass12345")
        self.medicine = Medicine.objects.create(name="Paracetamol")

    def test_create_order(self):
        o = Order.objects.create(
            facility=self.facility,
            requested_by=self.user,
            priority="urgent",
        )
        self.assertEqual(o.status, "pending")
        self.assertIn("Test Facility", str(o))

    def test_order_with_items(self):
        o = Order.objects.create(facility=self.facility, requested_by=self.user)
        OrderItem.objects.create(order=o, medicine=self.medicine, quantity=100)
        self.assertEqual(o.items.count(), 1)
        self.assertEqual(o.items.first().quantity, 100)


class DeliveryModelTest(TestCase):
    """Database tests for Delivery model."""

    def setUp(self):
        self.county = County.objects.create(name="Kisumu", code="KSM")
        self.facility = Facility.objects.create(name="Test Facility", county=self.county)
        self.hub = SupplyHub.objects.create(
            name="Test Hub",
            county=self.county,
            latitude=-0.10,
            longitude=34.75,
        )
        self.user = User.objects.create_user(username="testuser", password="pass12345")
        self.order = Order.objects.create(facility=self.facility, requested_by=self.user)

    def test_create_delivery(self):
        d = Delivery.objects.create(
            order=self.order,
            origin_hub=self.hub,
            destination_facility=self.facility,
            method="road",
        )
        self.assertEqual(d.status, "pending")
        self.assertEqual(d.method, "road")

    def test_delivery_drone_method(self):
        d = Delivery.objects.create(
            order=self.order,
            origin_hub=self.hub,
            destination_facility=self.facility,
            method="drone",
        )
        self.assertEqual(d.method, "drone")


class OrdersAPITest(TestCase):
    """API tests — verify the live dashboard endpoint returns correct JSON."""

    def setUp(self):
        self.client = Client()
        self.county = County.objects.create(name="Kisumu", code="KSM")
        self.facility = Facility.objects.create(name="Test Facility", county=self.county)
        self.user = User.objects.create_user(username="testuser", password="pass12345")

    def test_api_returns_empty_list(self):
        r = self.client.get(reverse('orders_api'))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertEqual(data['count'], 0)
        self.assertEqual(data['orders'], [])

    def test_api_returns_orders(self):
        Order.objects.create(
            facility=self.facility,
            requested_by=self.user,
            priority="urgent",
        )
        r = self.client.get(reverse('orders_api'))
        data = json.loads(r.content)
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['orders'][0]['facility'], "Test Facility")
        self.assertEqual(data['orders'][0]['priority'], "Urgent")

    def test_api_contains_required_fields(self):
        Order.objects.create(facility=self.facility, requested_by=self.user)
        r = self.client.get(reverse('orders_api'))
        data = json.loads(r.content)
        order = data['orders'][0]
        self.assertIn('id', order)
        self.assertIn('facility', order)
        self.assertIn('priority', order)
        self.assertIn('status', order)
        self.assertIn('requested_at', order)


class RealTimeDataTest(TestCase):
    """Real-time test — verify polling endpoint reflects new data."""

    def setUp(self):
        self.client = Client()
        self.county = County.objects.create(name="Kisumu", code="KSM")
        self.facility = Facility.objects.create(name="Test Facility", county=self.county)
        self.user = User.objects.create_user(username="testuser", password="pass12345")

    def test_new_order_appears_in_api(self):
        # First call - should be empty
        r1 = self.client.get(reverse('orders_api'))
        self.assertEqual(json.loads(r1.content)['count'], 0)

        # Create a new order (simulating what happens live)
        Order.objects.create(facility=self.facility, requested_by=self.user)

        # Second call - should now show 1
        r2 = self.client.get(reverse('orders_api'))
        self.assertEqual(json.loads(r2.content)['count'], 1)