"""
FleetOps Cloud — Core abstract models and tenant utilities.
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    created_at and updated_at fields.
    """

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantQuerySet(models.QuerySet):
    """
    QuerySet providing tenant-scoping methods.
    """

    def for_organization(self, organization):
        return self.filter(organization=organization)


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    """
    Manager enforcing or exposing tenant-scoped querysets.
    """
    pass


class TenantModel(TimeStampedModel):
    """
    Abstract base model for all resources belonging to an Organization.
    Enforces tenant scoping at the database and model layer.
    """

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )

    objects = TenantManager()

    class Meta:
        abstract = True
