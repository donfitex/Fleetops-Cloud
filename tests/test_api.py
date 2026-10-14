import re
from datetime import date

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.assignments.models import AssignmentStatus, VehicleAssignment
from apps.drivers.models import Driver
from apps.expenses.models import Expense
from apps.fleet.models import Vehicle
from apps.maintenance.models import MaintenanceStatus, WorkOrder
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
def test_viewer_cannot_create_vehicle(api_client, org_a):
    user = User.objects.create_user(
        email="viewer@example.com",
        password="StrongPassword123!",
        first_name="Viewer",
        last_name="User",
    )
    Membership.objects.create(
        user=user,
        organization=org_a,
        role=OrganizationRole.VIEWER,
    )

    api_client.force_authenticate(user=user)
    response = api_client.post(
        "/api/v1/vehicles/",
        {
            "registration_number": "API-400",
            "make": "Renault",
            "model": "Master",
            "year": 2024,
            "current_odometer": "8000",
        },
        format="json",
    )

    assert response.status_code == 403
    assert Vehicle.objects.filter(registration_number="API-400").count() == 0


@pytest.mark.django_db
def test_dashboard_summary_returns_tenant_metrics(api_client, user_a, org_a):
    vehicle = Vehicle.objects.create(
        organization=org_a,
        registration_number="API-500",
        make="Volvo",
        model="FH",
        year=2024,
        current_odometer=42000,
    )
    driver = Driver.objects.create(
        organization=org_a,
        first_name="Dana",
        last_name="Rivers",
        phone_number="555-0100",
        license_number="LIC-500",
        email="driver@fleetops.com",
    )
    VehicleAssignment.objects.create(
        organization=org_a,
        vehicle=vehicle,
        driver=driver,
        status=AssignmentStatus.ACTIVE,
    )
    WorkOrder.objects.create(
        organization=org_a,
        vehicle=vehicle,
        title="Brake inspection",
        maintenance_type="BRAKE_SERVICE",
        status=MaintenanceStatus.IN_PROGRESS,
        priority="HIGH",
        service_cost="250.00",
        odometer_reading=42050,
    )
    Expense.objects.create(
        organization=org_a,
        vehicle=vehicle,
        driver=driver,
        category="FUEL",
        title="Fuel top-up",
        amount="120.00",
        occurred_on=date.today(),
    )

    api_client.force_authenticate(user=user_a)
    response = api_client.get("/api/v1/dashboard/summary/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["totals"]["vehicles"] == 1
    assert payload["totals"]["drivers"] == 1
    assert payload["totals"]["active_assignments"] == 1
    assert payload["totals"]["open_work_orders"] == 1
    assert payload["totals"]["monthly_expense_total"] == 120.0


@pytest.mark.django_db
def test_dashboard_page_renders_summary(client, user_a, org_a):
    vehicle = Vehicle.objects.create(
        organization=org_a,
        registration_number="WEB-900",
        make="Isuzu",
        model="FTR",
        year=2023,
        current_odometer=28000,
    )
    driver = Driver.objects.create(
        organization=org_a,
        first_name="Alex",
        last_name="Smith",
        phone_number="555-1234",
        license_number="LIC-900",
    )
    VehicleAssignment.objects.create(
        organization=org_a,
        vehicle=vehicle,
        driver=driver,
        status=AssignmentStatus.ACTIVE,
    )
    WorkOrder.objects.create(
        organization=org_a,
        vehicle=vehicle,
        title="Tire check",
        maintenance_type="TIRES",
        status=MaintenanceStatus.IN_PROGRESS,
        priority="MEDIUM",
        service_cost="180.00",
        odometer_reading=28050,
    )
    Expense.objects.create(
        organization=org_a,
        vehicle=vehicle,
        driver=driver,
        category="FUEL",
        title="Fuel top-up",
        amount="90.00",
        occurred_on=date.today(),
    )

    client.force_login(user_a)
    response = client.get("/dashboard/")

    assert response.status_code == 200
    content = response.content.decode()
    assert "<title>Dashboard" in content
    assert re.search(r"<h1[^>]*>\s*Dashboard\s*</h1>", content)
    assert "API Tenant A" in content
    assert "1" in content


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
