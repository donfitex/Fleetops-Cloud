import pytest

from apps.accounts.models import User
from apps.organizations.models import Membership, Organization, OrganizationRole


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        email="operator@testfleet.com",
        password="TestPassword123!",
        first_name="Jane",
        last_name="Doe",
    )
    assert user.email == "operator@testfleet.com"
    assert user.check_password("TestPassword123!")
    assert user.full_name == "Jane Doe"
    assert user.is_active is True
    assert user.is_staff is False


@pytest.mark.django_db
def test_create_superuser():
    superuser = User.objects.create_superuser(
        email="admin@testfleet.com",
        password="AdminPassword123!",
    )
    assert superuser.is_staff is True
    assert superuser.is_superuser is True


@pytest.mark.django_db
def test_organization_and_membership():
    org = Organization.objects.create(name="Apex Transport")
    assert org.slug == "apex-transport"

    user = User.objects.create_user(
        email="manager@apextransport.com",
        password="TestPassword123!",
    )

    membership = Membership.objects.create(
        user=user,
        organization=org,
        role=OrganizationRole.FLEET_MANAGER,
    )

    assert membership.role == OrganizationRole.FLEET_MANAGER
    assert str(membership) == f"{user} - {org} (Fleet Manager)"
    assert org.memberships.count() == 1
