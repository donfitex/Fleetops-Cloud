import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.notifications.models import Notification, NotificationLevel
from apps.organizations.models import Membership, Organization, OrganizationRole


@pytest.fixture
def org_a(db):
    return Organization.objects.create(name="Notification Tenant A")


@pytest.fixture
def org_b(db):
    return Organization.objects.create(name="Notification Tenant B")


@pytest.fixture
def user_a(db, org_a):
    user = User.objects.create_user(
        email="notify-user@example.com",
        password="StrongPassword123!",
        first_name="Notify",
        last_name="User",
    )
    Membership.objects.create(
        user=user,
        organization=org_a,
        role=OrganizationRole.FLEET_MANAGER,
    )
    return user


@pytest.mark.django_db
def test_notification_creation_requires_active_membership(org_a, user_a):
    notification = Notification.objects.create(
        organization=org_a,
        user=user_a,
        title="Vehicle due for service",
        message="A vehicle in your fleet is approaching its maintenance window.",
        level=NotificationLevel.WARNING,
    )

    assert notification.organization == org_a
    assert notification.user == user_a
    assert notification.is_read is False


@pytest.mark.django_db
def test_notification_rejects_user_outside_tenant(org_a, org_b):
    other_org = org_b
    user = User.objects.create_user(
        email="outsider@example.com",
        password="StrongPassword123!",
        first_name="Outside",
        last_name="User",
    )
    Membership.objects.create(
        user=user,
        organization=other_org,
        role=OrganizationRole.VIEWER,
    )

    with pytest.raises(ValidationError):
        Notification.objects.create(
            organization=org_a,
            user=user,
            title="Wrong org notification",
            message="This should fail.",
            level=NotificationLevel.INFO,
        )
