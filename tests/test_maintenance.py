import pytest
from django.core.exceptions import ValidationError

from apps.fleet.models import Vehicle
from apps.maintenance.models import MaintenanceSchedule, MaintenanceStatus, WorkOrder
from apps.organizations.models import Organization


@pytest.fixture
def org_a(db):
    return Organization.objects.create(name="North Fleet Group")


@pytest.fixture
def org_b(db):
    return Organization.objects.create(name="South Fleet Group")


@pytest.fixture
def vehicle_a(db, org_a):
    return Vehicle.objects.create(
        organization=org_a,
        registration_number="MA-100",
        make="Mercedes",
        model="Sprinter",
        year=2023,
    )


@pytest.fixture
def vehicle_b(db, org_b):
    return Vehicle.objects.create(
        organization=org_b,
        registration_number="MA-200",
        make="Volvo",
        model="VNL",
        year=2024,
    )


@pytest.mark.django_db
def test_maintenance_schedule_and_work_order_creation(org_a, vehicle_a):
    schedule = MaintenanceSchedule.objects.create(
        organization=org_a,
        vehicle=vehicle_a,
        title="Oil Change",
        interval_days=180,
        interval_km=8000,
        next_due_date="2026-11-01",
        next_due_odometer=20500,
    )

    work_order = WorkOrder.objects.create(
        organization=org_a,
        vehicle=vehicle_a,
        schedule=schedule,
        title="Service oil change",
        status=MaintenanceStatus.SCHEDULED,
        service_cost=245.50,
        odometer_reading=20500,
        vendor_name="FleetCare Garage",
    )

    assert schedule.title == "Oil Change"
    assert work_order.schedule == schedule
    assert work_order.vehicle == vehicle_a
    assert work_order.organization == org_a


@pytest.mark.django_db
def test_work_order_rejects_cross_tenant_schedule(org_a, org_b, vehicle_a, vehicle_b):
    schedule = MaintenanceSchedule.objects.create(
        organization=org_b,
        vehicle=vehicle_b,
        title="Brake Check",
    )

    with pytest.raises(ValidationError):
        WorkOrder.objects.create(
            organization=org_a,
            vehicle=vehicle_a,
            schedule=schedule,
            title="Brake service",
        )


@pytest.mark.django_db
def test_maintenance_work_order_requires_valid_dates(org_a, vehicle_a):
    schedule = MaintenanceSchedule.objects.create(
        organization=org_a,
        vehicle=vehicle_a,
        title="Inspection",
        next_due_date="2026-10-15",
    )

    with pytest.raises(ValidationError):
        WorkOrder.objects.create(
            organization=org_a,
            vehicle=vehicle_a,
            schedule=schedule,
            title="Inspection completed early",
            scheduled_date="2026-10-20",
            completed_at="2026-10-10T09:00:00Z",
        )
