import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.fleet.models import Vehicle
from apps.organizations.models import Membership, Organization, OrganizationRole


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def org_a(db):
    return Organization.objects.create(name="API Tenant A")


@pytest.fixture
def org_b(db):
    return Organization.objects.create(name="API Tenant B")


@pytest.fixture
def user_a(db, org_a):
    user = User.objects.create_user(
        email="api-user@example.com",
        password="StrongPassword123!",
        first_name="API",
        last_name="User",
    )
    Membership.objects.create(
        user=user,
        organization=org_a,
        role=OrganizationRole.FLEET_MANAGER,
    )
    return user


@pytest.mark.django_db
def test_vehicle_api_lists_only_current_organization(api_client, user_a, org_a, org_b):
    v1 = Vehicle.objects.create(
        organization=org_a,
        registration_number="API-100",
        make="Ford",
        model="Transit",
        year=2024,
    )
    Vehicle.objects.create(
        organization=org_b,
        registration_number="API-200",
        make="Mercedes",
        model="Sprinter",
        year=2025,
    )

    api_client.force_authenticate(user=user_a)
    response = api_client.get("/api/v1/vehicles/")

    assert response.status_code == 200
    payload = response.json()
    results = payload["results"]
    assert len(results) == 1
    assert results[0]["id"] == v1.id
    assert results[0]["registration_number"] == "API-100"


@pytest.mark.django_db
def test_vehicle_api_create_scopes_record_to_user_org(api_client, user_a, org_a):
    api_client.force_authenticate(user=user_a)
    response = api_client.post(
        "/api/v1/vehicles/",
        {
            "registration_number": "API-300",
            "make": "Volkswagen",
            "model": "Crafter",
            "year": 2023,
            "current_odometer": "12000.50",
        },
        format="json",
    )

    assert response.status_code == 201
    vehicle = Vehicle.objects.get(pk=response.json()["id"])
    assert vehicle.organization == org_a
    assert vehicle.registration_number == "API-300"


@pytest.mark.django_db
def test_token_login_returns_auth_token(api_client, user_a):
    response = api_client.post(
        "/api/v1/auth/login/",
        {"email": user_a.email, "password": "StrongPassword123!"},
        format="json",
    )

    assert response.status_code == 200
    payload = response.json()
    assert "token" in payload
    assert payload["user"]["email"] == user_a.email
