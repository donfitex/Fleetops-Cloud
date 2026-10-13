from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.models import TenantModel


class MaintenanceType(models.TextChoices):
    OIL_CHANGE = "OIL_CHANGE", "Oil Change"
    BRAKE_SERVICE = "BRAKE_SERVICE", "Brake Service"
    INSPECTION = "INSPECTION", "Inspection"
    TIRES = "TIRES", "Tires"
    ENGINE = "ENGINE", "Engine"
    GENERAL = "GENERAL", "General Service"
    OTHER = "OTHER", "Other"


class MaintenanceStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    OVERDUE = "OVERDUE", "Overdue"


class WorkOrderPriority(models.TextChoices):
    LOW = "LOW", "Low"
    MEDIUM = "MEDIUM", "Medium"
    HIGH = "HIGH", "High"
    CRITICAL = "CRITICAL", "Critical"


class MaintenanceSchedule(TenantModel):
    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.CASCADE,
        related_name="maintenance_schedules",
    )
    title = models.CharField(max_length=200)
    maintenance_type = models.CharField(
        max_length=30,
        choices=MaintenanceType.choices,
        default=MaintenanceType.GENERAL,
    )
    interval_days = models.PositiveIntegerField(default=30)
    interval_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    next_due_date = models.DateField(default=timezone.now)
    next_due_odometer = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "maintenance schedule"
        verbose_name_plural = "maintenance schedules"
        ordering = ["next_due_date", "title"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "vehicle", "title"],
                name="unique_maintenance_schedule_per_vehicle_title",
            )
        ]

    def __str__(self):
        return f"{self.title} ({self.vehicle.registration_number})"


class WorkOrder(TenantModel):
    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.CASCADE,
        related_name="work_orders",
    )
    schedule = models.ForeignKey(
        "MaintenanceSchedule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders",
    )
    title = models.CharField(max_length=200)
    maintenance_type = models.CharField(
        max_length=30,
        choices=MaintenanceType.choices,
        default=MaintenanceType.GENERAL,
    )
    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.SCHEDULED,
        db_index=True,
    )
    priority = models.CharField(
        max_length=20,
        choices=WorkOrderPriority.choices,
        default=WorkOrderPriority.MEDIUM,
        db_index=True,
    )
    requested_at = models.DateTimeField(default=timezone.now, db_index=True)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    service_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    odometer_reading = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    vendor_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "work order"
        verbose_name_plural = "work orders"
        ordering = ["-requested_at"]

    def clean(self):
        super().clean()

        if self.schedule:
            if self.schedule.organization_id != self.organization_id:
                raise ValidationError({
                    "schedule": (
                        "The selected maintenance schedule does not belong to this organization."
                    )
                })
            if self.schedule.vehicle_id != self.vehicle_id:
                raise ValidationError({
                    "schedule": "The selected maintenance schedule is not for this vehicle."
                })

        if self.scheduled_date and self.completed_at:
            completed_date = self.completed_at.date()
            if completed_date < self.scheduled_date:
                raise ValidationError({
                    "completed_at": "Completion date cannot be earlier than the scheduled date."
                })

        if self.completed_at and self.requested_at and self.completed_at < self.requested_at:
            raise ValidationError({
                "completed_at": "Completion time cannot be earlier than the request time."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.vehicle.registration_number})"
