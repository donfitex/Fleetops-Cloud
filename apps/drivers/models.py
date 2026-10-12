"""
FleetOps Cloud — Driver Models.
Tenant-scoped driver management.
"""

from django.conf import settings
from django.db import models

from apps.core.models import TenantModel


class DriverStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    ON_LEAVE = "ON_LEAVE", "On Leave"
    SUSPENDED = "SUSPENDED", "Suspended"
    TERMINATED = "TERMINATED", "Terminated"


class Driver(TenantModel):
    """
    Driver employed or contracted by an Organization.
    Optionally linked to a User account if the driver has platform login access.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driver_profiles",
        help_text="Optional login user account for this driver.",
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=30)
    license_number = models.CharField(
        max_length=100,
        help_text="Driver's official license number.",
        db_index=True,
    )
    license_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="License category/class (e.g. Class C, Commercial, Heavy Goods).",
    )
    license_expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date on which the driver license expires.",
    )
    status = models.CharField(
        max_length=20,
        choices=DriverStatus.choices,
        default=DriverStatus.ACTIVE,
        db_index=True,
    )

    class Meta:
        verbose_name = "driver"
        verbose_name_plural = "drivers"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "license_number"],
                name="unique_driver_license_per_organization",
            )
        ]
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.license_number})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
