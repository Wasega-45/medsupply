from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
import time

from .models import County, Facility, Medicine, Inventory, SupplyHub, haversine_distance


class HaversineDistanceTest(TestCase):
    """Unit tests for the Haversine distance calculation."""

    def test_same_point_is_zero(self):
        d = haversine_distance(-0.0917, 34.7680, -0.0917, 34.7680)
        self.assertAlmostEqual(d, 0, places=2)

    def test_kisumu_to_nairobi(self):
        d = haversine_distance(-0.0917, 34.7680, -1.2864, 36.8172)
        self.assertTrue(255 < d < 275, f"Expected ~265 km, got {d:.2f} km")

    def test_short_distance(self):
        d = haversine_distance(-0.0917, 34.7680, -0.1000, 34.7500)
        self.assertTrue(0 < d < 5, f"Expected 0-5 km, got {d:.2f} km")


class CountyModelTest(TestCase):
    """Database tests for County model."""

    def test_create_county(self):
        c = County.objects.create(name="Kisumu", code="KSM")
        self.assertEqual(str(c), "Kisumu")
        self.assertEqual(County.objects.count(), 1)

    def test_county_unique_name(self):
        County.objects.create(name="Kisumu", code="KSM")
        with self.assertRaises(Exception):
            County.objects.create(name="Kisumu", code="OTHER")


class FacilityModelTest(TestCase):
    """Database tests for Facility model."""

    def setUp(self):
        self.county = County.objects.create(name="Kisumu", code="KSM")

    def test_create_facility(self):
        f = Facility.objects.create(
            name="Test Hospital",
            county=self.county,
            facility_type="hospital",
        )
        self.assertIn("Test Hospital", str(f))
        self.assertEqual(f.county, self.county)

    def test_facility_default_status(self):
        f = Facility.objects.create(name="Test", county=self.county)
        self.assertEqual(f.status, "active")


class SpatialAnalysisTest(TestCase):
    """Spatial analysis tests — coverage, distance, nearest hub."""

    def setUp(self):
        self.county = County.objects.create(name="Kisumu", code="KSM")
        self.hub = SupplyHub.objects.create(
            name="Test Hub",
            county=self.county,
            latitude=-0.1000,
            longitude=34.7500,
            service_radius_km=50,
            active=True,
        )
        self.facility_inside = Facility.objects.create(
            name="Inside Facility",
            county=self.county,
            latitude=-0.0917,
            longitude=34.7680,
        )
        self.facility_outside = Facility.objects.create(
            name="Outside Facility",
            county=self.county,
            latitude=-1.2864,
            longitude=36.8172,
        )

    def test_facility_inside_coverage(self):
        self.assertTrue(self.facility_inside.is_covered())

    def test_facility_outside_coverage(self):
        self.assertFalse(self.facility_outside.is_covered())

    def test_nearest_hub(self):
        hub, dist = self.facility_inside.nearest_hub()
        self.assertEqual(hub, self.hub)
        self.assertIsNotNone(dist)

    def test_no_coordinates_returns_none(self):
        f = Facility.objects.create(name="No Coords", county=self.county)
        hub, dist = f.nearest_hub()
        self.assertIsNone(hub)
        self.assertIsNone(dist)


class InventoryModelTest(TestCase):
    """Database tests for Inventory."""

    def setUp(self):
        self.county = County.objects.create(name="Kisumu", code="KSM")
        self.facility = Facility.objects.create(name="F1", county=self.county)
        self.medicine = Medicine.objects.create(name="Paracetamol")

    def test_create_inventory(self):
        inv = Inventory.objects.create(
            facility=self.facility,
            medicine=self.medicine,
            quantity=500,
        )
        self.assertEqual(inv.quantity, 500)
        self.assertEqual(inv.reserved_quantity, 0)

    def test_unique_together(self):
        Inventory.objects.create(facility=self.facility, medicine=self.medicine, quantity=100)
        with self.assertRaises(Exception):
            Inventory.objects.create(facility=self.facility, medicine=self.medicine, quantity=200)


class UIPageLoadTest(TestCase):
    """UI test — verify pages return 200 status."""

    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        r = self.client.get(reverse('home'))
        self.assertEqual(r.status_code, 200)

    def test_map_page_loads(self):
        r = self.client.get(reverse('facility_map'))
        self.assertEqual(r.status_code, 200)

    def test_orders_page_loads(self):
        r = self.client.get(reverse('order_list'))
        self.assertEqual(r.status_code, 200)

    def test_deliveries_page_loads(self):
        r = self.client.get(reverse('delivery_list'))
        self.assertEqual(r.status_code, 200)

    def test_coverage_page_loads(self):
        r = self.client.get(reverse('coverage_report'))
        self.assertEqual(r.status_code, 200)


class PerformanceTest(TestCase):
    """Basic performance test — queries should complete quickly."""

    def setUp(self):
        self.county = County.objects.create(name="Kisumu", code="KSM")
        for i in range(50):
            Facility.objects.create(
                name=f"Facility {i}",
                county=self.county,
                latitude=-0.0917 + (i * 0.01),
                longitude=34.7680 + (i * 0.01),
            )

    def test_facility_query_is_fast(self):
        start = time.time()
        list(Facility.objects.all())
        elapsed = time.time() - start
        self.assertLess(elapsed, 1.0, f"Query took {elapsed:.2f}s — too slow")