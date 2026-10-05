from django.db import models
from math import radians, sin, cos, sqrt, atan2


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance in kilometers between two lat/lng points."""
    R = 6371  # Earth's radius in km

    lat1_r, lon1_r = radians(float(lat1)), radians(float(lon1))
    lat2_r, lon2_r = radians(float(lat2)), radians(float(lon2))

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = sin(dlat / 2) ** 2 + cos(lat1_r) * cos(lat2_r) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name_plural = "Counties"
        ordering = ['name']

    def __str__(self):
        return self.name


class Facility(models.Model):
    FACILITY_TYPES = [
        ('dispensary', 'Dispensary'),
        ('health_centre', 'Health Centre'),
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=150)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES, default='dispensary')
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='facilities')
    location = models.CharField(max_length=255, blank=True, help_text="Description of location")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        verbose_name_plural = "Facilities"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()})"

    def nearest_hub(self):
        """Find the nearest active supply hub and the distance in km."""
        hubs = SupplyHub.objects.filter(active=True)
        nearest = None
        min_dist = None

        if self.latitude is None or self.longitude is None:
            return None, None

        for hub in hubs:
            d = haversine_distance(self.latitude, self.longitude, hub.latitude, hub.longitude)
            if min_dist is None or d < min_dist:
                min_dist = d
                nearest = hub

        return nearest, min_dist

    def is_covered(self):
        """Check if this facility is within the nearest hub's service radius."""
        hub, dist = self.nearest_hub()
        if hub is None or dist is None:
            return False
        return dist <= hub.service_radius_km


class Medicine(models.Model):
    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=30, default='units', help_text="e.g., tablets, vials, bottles")
    reorder_level = models.PositiveIntegerField(default=10, help_text="Minimum stock before reorder")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Inventory(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, related_name='inventory')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='inventory')
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Inventory"
        unique_together = ('facility', 'medicine')

    def __str__(self):
        return f"{self.medicine.name} @ {self.facility.name}: {self.quantity}"


class SupplyHub(models.Model):
    name = models.CharField(max_length=150)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='hubs')
    location = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    service_radius_km = models.PositiveIntegerField(default=50, help_text="Coverage radius in km")
    contact = models.CharField(max_length=50, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Supply Hubs"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.county.name})"