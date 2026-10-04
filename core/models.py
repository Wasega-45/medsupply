from django.db import models


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