"""
FleetOps Cloud — Organization and Membership Models.
Tenant root definitions and Role-Based Access Control (RBAC).
"""

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


class OrganizationRole(models.TextChoices):
    OWNER = "OWNER", "Owner"
    ADMIN = "ADMIN", "Administrator"
    FLEET_MANAGER = "FLEET_MANAGER", "Fleet Manager"
    DRIVER = "DRIVER", "Driver"
    VIEWER = "VIEWER", "Viewer"


class Organization(TimeStampedModel):
    """
    The tenant boundary. All fleet vehicles, drivers, expenses,
    and records are owned by an Organization.
    """

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "organization"
        verbose_name_plural = "organizations"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Organization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Membership(TimeStampedModel):
    """
    Represents a user's membership and specific role within an Organization.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=OrganizationRole.choices,
        default=OrganizationRole.VIEWER,
        db_index=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "membership"
        verbose_name_plural = "memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_organization_membership",
            )
        ]
        ordering = ["organization", "user"]

    def __str__(self):
        return f"{self.user} - {self.organization} ({self.get_role_display()})"

    @property
    def is_owner(self):
        return self.role == OrganizationRole.OWNER

    @property
    def is_admin(self):
        return self.role == OrganizationRole.ADMIN

    @property
    def is_fleet_manager(self):
        return self.role == OrganizationRole.FLEET_MANAGER

    @property
    def is_driver(self):
        return self.role == OrganizationRole.DRIVER

    @property
    def is_viewer(self):
        return self.role == OrganizationRole.VIEWER

    @property
    def can_read(self):
        return self.is_active

    @property
    def can_write(self):
        return self.role in {
            OrganizationRole.OWNER,
            OrganizationRole.ADMIN,
            OrganizationRole.FLEET_MANAGER,
        }
