import pytest
from django.core.exceptions import ValidationError

from apps.assignments.models import AssignmentStatus, VehicleAssignment
from apps.drivers.models import Driver
from apps.fleet.models import Vehicle
from apps.organizations.models import Organization


@pytest.fixture
def org_a(db):
    return Organization.objects.create(name="TransLogistics North")


@pytest.fixture
def org_b(db):
    return Organization.objects.create(name="Metro Express South")


@pytest.fixture
def vehicle_a(db, org_a):
    return Vehicle.objects.create(
        organization=org_a,
        registration_number="AB12 CDE",
        make="Ford",
        model="Transit",
        year=2022,
        current_odometer=15000.0,
    )


@pytest.fixture
def driver_a(db, org_a):
    return Driver.objects.create(
        organization=org_a,
        first_name="John",
        last_name="Smith",
        license_number="SMITH123456",
        phone_number="+44 7700 900077",
    )


@pytest.mark.django_db
def test_vehicle_creation_and_tenant_uniqueness(org_a, org_b):
    v1 = Vehicle.objects.create(
        organization=org_a,
        registration_number="REG-101",
        make="Toyota",
        model="Hilux",
        year=2021,
    )
    assert v1.registration_number == "REG-101"
    assert v1.organization == org_a

    # Another organization can have the exact same registration number without collision
    v2 = Vehicle.objects.create(
        organization=org_b,
        registration_number="REG-101",
        make="Toyota",
        model="Hilux",
        year=2021,
    )
    assert v2.organization == org_b

    from django.db import IntegrityError
    # But the same organization cannot have duplicate registrations
    with pytest.raises(IntegrityError):
        Vehicle.objects.create(
            organization=org_a,
            registration_number="REG-101",
            make="Toyota",
            model="Hilux",
            year=2023,
        )


@pytest.mark.django_db
def test_tenant_queryset_isolation(org_a, org_b, vehicle_a):
    Vehicle.objects.create(
        organization=org_b,
        registration_number="XY99 ZZZ",
        make="Volvo",
        model="FH16",
        year=2024,
    )

    org_a_vehicles = Vehicle.objects.for_organization(org_a)
    assert org_a_vehicles.count() == 1
    assert org_a_vehicles.first() == vehicle_a

    org_b_vehicles = Vehicle.objects.for_organization(org_b)
    assert org_b_vehicles.count() == 1
    assert org_b_vehicles.first().registration_number == "XY99 ZZZ"


@pytest.mark.django_db
def test_valid_vehicle_assignment(org_a, vehicle_a, driver_a):
    assignment = VehicleAssignment.objects.create(
        organization=org_a,
        vehicle=vehicle_a,
        driver=driver_a,
        status=AssignmentStatus.ACTIVE,
    )
    assert assignment.status == AssignmentStatus.ACTIVE
    assert assignment.vehicle == vehicle_a
    assert assignment.driver == driver_a


@pytest.mark.django_db
def test_cross_tenant_assignment_blocked(org_a, org_b, vehicle_a):
    # Driver belongs to org_b, vehicle belongs to org_a
    driver_b = Driver.objects.create(
        organization=org_b,
        first_name="Cross",
        last_name="Driver",
        license_number="CROSS999",
        phone_number="+44 7700 900088",
    )

    with pytest.raises(ValidationError):
        VehicleAssignment.objects.create(
            organization=org_a,
            vehicle=vehicle_a,
            driver=driver_b,
            status=AssignmentStatus.ACTIVE,
        )


@pytest.mark.django_db
def test_conflicting_active_assignment_prevented(org_a, vehicle_a, driver_a):
    # Active assignment 1
    VehicleAssignment.objects.create(
        organization=org_a,
        vehicle=vehicle_a,
        driver=driver_a,
        status=AssignmentStatus.ACTIVE,
    )

    # Driver 2 attempting to take the same vehicle while assignment 1 is active
    driver_2 = Driver.objects.create(
        organization=org_a,
        first_name="Second",
        last_name="Driver",
        license_number="DRIVER2_LIC",
        phone_number="+44 7700 900099",
    )

    with pytest.raises(ValidationError) as exc:
        VehicleAssignment.objects.create(
            organization=org_a,
            vehicle=vehicle_a,
            driver=driver_2,
            status=AssignmentStatus.ACTIVE,
        )
    assert "already has an active assignment" in str(exc.value)
