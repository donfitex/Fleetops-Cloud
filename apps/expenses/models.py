from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TenantModel


class ExpenseCategory(models.TextChoices):
    FUEL = "FUEL", "Fuel"
    MAINTENANCE = "MAINTENANCE", "Maintenance"
    INSURANCE = "INSURANCE", "Insurance"
    TOLLS = "TOLLS", "Tolls"
    PARKING = "PARKING", "Parking"
    TIRES = "TIRES", "Tires"
    REGISTRATION = "REGISTRATION", "Registration"
    OTHER = "OTHER", "Other"


class Expense(TenantModel):
    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    category = models.CharField(
        max_length=30,
        choices=ExpenseCategory.choices,
        default=ExpenseCategory.OTHER,
        db_index=True,
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    occurred_on = models.DateField(default=timezone.now, db_index=True)
    vendor_name = models.CharField(max_length=200, blank=True)
    receipt_reference = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "expense"
        verbose_name_plural = "expenses"
        ordering = ["-occurred_on", "-created_at"]

    def clean(self):
        super().clean()

        if self.vehicle and self.vehicle.organization_id != self.organization_id:
            raise ValidationError({
                "vehicle": "The selected vehicle does not belong to this organization."
            })

        if self.driver and self.driver.organization_id != self.organization_id:
            raise ValidationError({
                "driver": "The selected driver does not belong to this organization."
            })

        if (
            self.vehicle
            and self.driver
            and self.vehicle.organization_id != self.driver.organization_id
        ):
            raise ValidationError({
                "driver": "The selected driver and vehicle must belong to the same organization."
            })

        if self.amount < 0:
            raise ValidationError({
                "amount": "Expense amount cannot be negative."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.amount} ({self.category})"
