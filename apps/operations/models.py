from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TenantModel


class FuelType(models.TextChoices):
    PETROL = "PETROL", "Petrol"
    DIESEL = "DIESEL", "Diesel"
    HYBRID = "HYBRID", "Hybrid"
    ELECTRIC = "ELECTRIC", "Electric"
    LPG = "LPG", "LPG"


class TripStatus(models.TextChoices):
    PLANNED = "PLANNED", "Planned"
    ACTIVE = "ACTIVE", "Active"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class FuelLog(TenantModel):
    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.CASCADE,
        related_name="fuel_logs",
    )
    fuel_type = models.CharField(
        max_length=20,
        choices=FuelType.choices,
        default=FuelType.DIESEL,
    )
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.001"))],
    )
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    odometer_reading = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    refilled_at = models.DateTimeField(default=timezone.now, db_index=True)
    vendor_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "fuel log"
        verbose_name_plural = "fuel logs"
        ordering = ["-refilled_at"]

    def clean(self):
        super().clean()
        cost_differs = (
            self.total_cost
            and self.quantity
            and self.unit_cost
            and self.total_cost != self.quantity * self.unit_cost
        )
        if cost_differs:
            raise ValidationError({
                "total_cost": "Total cost must equal quantity multiplied by unit cost."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.total_cost and self.quantity and self.unit_cost:
            self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle.registration_number} — {self.quantity}L @ {self.total_cost}"


class Trip(TenantModel):
    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.CASCADE,
        related_name="trips",
    )
    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trips",
    )
    status = models.CharField(
        max_length=20,
        choices=TripStatus.choices,
        default=TripStatus.PLANNED,
        db_index=True,
    )
    start_time = models.DateTimeField(default=timezone.now, db_index=True)
    end_time = models.DateTimeField(null=True, blank=True, db_index=True)
    start_odometer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    end_odometer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    route_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "trip"
        verbose_name_plural = "trips"
        ordering = ["-start_time"]

    def clean(self):
        super().clean()

        if self.driver and self.driver.organization_id != self.organization_id:
            raise ValidationError({
                "driver": "The selected driver does not belong to this organization."
            })

        if self.driver and self.vehicle.organization_id != self.organization_id:
            raise ValidationError({
                "vehicle": "The selected vehicle does not belong to this organization."
            })

        if (
            self.vehicle_id
            and self.driver
            and self.vehicle.organization_id != self.driver.organization_id
        ):
            raise ValidationError({
                "vehicle": "The selected vehicle and driver must belong to the same organization."
            })

        if self.end_odometer and self.start_odometer and self.end_odometer < self.start_odometer:
            raise ValidationError({
                "end_odometer": "End odometer cannot be lower than the start odometer."
            })

        if self.end_time and self.start_time and self.end_time < self.start_time:
            raise ValidationError({
                "end_time": "Trip end time cannot precede the start time."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def distance_km(self):
        if self.end_odometer and self.start_odometer:
            return max(Decimal("0.00"), self.end_odometer - self.start_odometer)
        return Decimal("0.00")

    def __str__(self):
        return f"{self.vehicle.registration_number} - {self.start_time.date()}"
