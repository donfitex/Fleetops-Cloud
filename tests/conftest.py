import pytest

from apps.accounts.models import User
from apps.organizations.models import Membership, Organization, OrganizationRole


@pytest.fixture
def user_factory(db):
    def create_user(email="user@fleetops.com", password="SecurePassword123!", **kwargs):
        return User.objects.create_user(email=email, password=password, **kwargs)
    return create_user


@pytest.fixture
def organization_factory(db):
    def create_org(name="Acme Logistics", **kwargs):
        return Organization.objects.create(name=name, **kwargs)
    return create_org


@pytest.fixture
def membership_factory(db, user_factory, organization_factory):
    def create_membership(user=None, organization=None, role=OrganizationRole.VIEWER, **kwargs):
        if user is None:
            user = user_factory()
        if organization is None:
            organization = organization_factory()
        return Membership.objects.create(user=user, organization=organization, role=role, **kwargs)
    return create_membership
