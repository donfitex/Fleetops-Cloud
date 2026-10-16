from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import TenantModel
from apps.organizations.models import Membership, Organization


class NotificationLevel(models.TextChoices):
    INFO = "INFO", "Info"
    SUCCESS = "SUCCESS", "Success"
    WARNING = "WARNING", "Warning"
    ERROR = "ERROR", "Error"


class Notification(TenantModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(
        max_length=20,
        choices=NotificationLevel.choices,
        default=NotificationLevel.INFO,
        db_index=True,
    )
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    link = models.URLField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"
        ordering = ["-created_at"]

    def clean(self):
        super().clean()

        if self.organization_id and self.user_id:
            active_membership = Membership.objects.filter(
                user_id=self.user_id,
                organization_id=self.organization_id,
                is_active=True,
            ).exists()
            if not active_membership:
                raise ValidationError(
                    {"user": "The selected user is not a member of this organization."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.user.email})"
