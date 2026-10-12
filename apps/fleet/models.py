"""
FleetOps Cloud — Vehicle Models.
Tenant-scoped vehicle management.
"""

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TenantModel


class VehicleStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    MAINTENANCE = "MAINTENANCE", "In Maintenance"
    OUT_OF_SERVICE = "OUT_OF_SERVICE", "Out of Service"
    RETIRED = "RETIRED", "Retired"


class FuelType(models.TextChoices):
    DIESEL = "DIESEL", "Diesel"
    PETROL = "PETROL", "Petrol"
    ELECTRIC = "ELECTRIC", "Electric"
    HYBRID = "HYBRID", "Hybrid"
    OTHER = "OTHER", "Other"


class Vehicle(TenantModel):
    """
    Vehicle asset owned by an Organization.
    """

    registration_number = models.CharField(
        max_length=50,
        help_text="License plate / vehicle registration number.",
        db_index=True,
    )
    vin = models.CharField(
        max_length=17,
        blank=True,
        verbose_name="VIN",
        help_text="17-character Vehicle Identification Number.",
    )
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(1900)],
        help_text="Model manufacturing year.",
    )
    status = models.CharField(
        max_length=20,
        choices=VehicleStatus.choices,
        default=VehicleStatus.ACTIVE,
        db_index=True,
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=FuelType.choices,
        default=FuelType.DIESEL,
    )
    current_odometer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0)],
        help_text="Current odometer reading in km or miles.",
    )

    class Meta:
        verbose_name = "vehicle"
        verbose_name_plural = "vehicles"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "registration_number"],
                name="unique_vehicle_registration_per_organization",
            )
        ]
        ordering = ["registration_number"]

    def __str__(self):
        return f"{self.registration_number} — {self.make} {self.model} ({self.year})"
