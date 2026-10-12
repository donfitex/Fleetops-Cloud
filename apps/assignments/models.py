"""
FleetOps Cloud — Vehicle Assignment Models.
Manages driver-vehicle assignments with tenant isolation and conflict prevention.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TenantModel


class AssignmentStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    COMPLETED = "COMPLETED", "Completed"
    SCHEDULED = "SCHEDULED", "Scheduled"
    CANCELLED = "CANCELLED", "Cancelled"


class VehicleAssignment(TenantModel):
    """
    Assignment of a vehicle to a driver within an Organization.
    """

    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    start_time = models.DateTimeField(default=timezone.now, db_index=True)
    end_time = models.DateTimeField(null=True, blank=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=AssignmentStatus.choices,
        default=AssignmentStatus.ACTIVE,
        db_index=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "vehicle assignment"
        verbose_name_plural = "vehicle assignments"
        ordering = ["-start_time"]

    def clean(self):
        super().clean()
        # Tenant isolation validation: Vehicle and Driver must belong to the exact same organization
        if self.vehicle and self.driver:
            if self.vehicle.organization_id != self.organization_id:
                raise ValidationError({
                    "vehicle": "The selected vehicle does not belong to this organization."
                })
            if self.driver.organization_id != self.organization_id:
                raise ValidationError({
                    "driver": "The selected driver does not belong to this organization."
                })

        # Start and end time sanity check
        if self.end_time and self.start_time and self.end_time < self.start_time:
            raise ValidationError({
                "end_time": "Assignment end time cannot precede the start time."
            })

        # Prevent double-booking active vehicles in the same organization
        if self.status == AssignmentStatus.ACTIVE:
            conflicting_vehicle = (
                VehicleAssignment.objects.filter(
                    organization=self.organization,
                    vehicle=self.vehicle,
                    status=AssignmentStatus.ACTIVE,
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if conflicting_vehicle:
                raise ValidationError({
                    "vehicle": "This vehicle already has an active assignment."
                })

            conflicting_driver = (
                VehicleAssignment.objects.filter(
                    organization=self.organization,
                    driver=self.driver,
                    status=AssignmentStatus.ACTIVE,
                )
                .exclude(pk=self.pk)
                .exists()
            )
            if conflicting_driver:
                raise ValidationError({
                    "driver": "This driver is already assigned to another active vehicle."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle.registration_number} -> {self.driver.full_name} ({self.status})"
