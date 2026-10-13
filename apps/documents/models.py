from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import TenantModel


class DocumentCategory(models.TextChoices):
    VEHICLE = "VEHICLE", "Vehicle"
    DRIVER = "DRIVER", "Driver"
    INSURANCE = "INSURANCE", "Insurance"
    REGISTRATION = "REGISTRATION", "Registration"
    COMPLIANCE = "COMPLIANCE", "Compliance"
    OTHER = "OTHER", "Other"


class DocumentStatus(models.TextChoices):
    UPLOADED = "UPLOADED", "Uploaded"
    VERIFIED = "VERIFIED", "Verified"
    EXPIRED = "EXPIRED", "Expired"
    REJECTED = "REJECTED", "Rejected"


class FleetDocument(TenantModel):
    vehicle = models.ForeignKey(
        "fleet.Vehicle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    category = models.CharField(
        max_length=30,
        choices=DocumentCategory.choices,
        default=DocumentCategory.OTHER,
        db_index=True,
    )
    title = models.CharField(max_length=200)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    storage_path = models.CharField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.UPLOADED,
        db_index=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "fleet document"
        verbose_name_plural = "fleet documents"
        ordering = ["-created_at"]

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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class AuditTrail(TenantModel):
    entity_type = models.CharField(max_length=80)
    entity_id = models.BigIntegerField()
    action = models.CharField(max_length=80)
    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_trails",
    )
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "audit trail"
        verbose_name_plural = "audit trails"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} {self.action}"
