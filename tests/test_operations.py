import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.drivers.models import Driver
from apps.fleet.models import Vehicle
from apps.operations.models import FuelLog, FuelType, Trip, TripStatus
from apps.organizations.models import Organization


@pytest.fixture
def org_a(db):
    return Organization.objects.create(name="North Logistics")


@pytest.fixture
def org_b(db):
    return Organization.objects.create(name="South Logistics")


@pytest.fixture
def vehicle_a(db, org_a):
    return Vehicle.objects.create(
        organization=org_a,
        registration_number="OP-101",
        make="Ford",
        model="Transit",
        year=2022,
    )


@pytest.fixture
def vehicle_b(db, org_b):
    return Vehicle.objects.create(
        organization=org_b,
        registration_number="OP-202",
        make="Renault",
        model="Master",
        year=2023,
    )


@pytest.fixture
def driver_a(db, org_a):
    return Driver.objects.create(
        organization=org_a,
        first_name="Alex",
        last_name="Green",
        license_number="ALEX-100",
        phone_number="+44 7700 900111",
    )


@pytest.fixture
def driver_b(db, org_b):
    return Driver.objects.create(
        organization=org_b,
        first_name="Sam",
        last_name="Blue",
        license_number="SAM-200",
        phone_number="+44 7700 900222",
    )


@pytest.mark.django_db
def test_fuel_log_creation_and_total_cost(org_a, vehicle_a):
    log = FuelLog.objects.create(
        organization=org_a,
        vehicle=vehicle_a,
        fuel_type=FuelType.DIESEL,
        quantity=Decimal("45.500"),
        unit_cost=Decimal("1.62"),
        odometer_reading=Decimal("22100.00"),
        vendor_name="Apex Fuel",
    )

    assert log.total_cost == Decimal("73.71")
    assert log.organization == org_a
    assert log.vehicle == vehicle_a


@pytest.mark.django_db
def test_trip_rejects_invalid_odometer_and_cross_tenant_driver(org_a, org_b, vehicle_a, vehicle_b, driver_a, driver_b):
    with pytest.raises(ValidationError):
        Trip.objects.create(
            organization=org_a,
            vehicle=vehicle_a,
            driver=driver_b,
            status=TripStatus.ACTIVE,
            start_odometer=Decimal("15000.00"),
            end_odometer=Decimal("14800.00"),
        )

    with pytest.raises(ValidationError):
        Trip.objects.create(
            organization=org_a,
            vehicle=vehicle_a,
            driver=driver_a,
            status=TripStatus.ACTIVE,
            start_odometer=Decimal("15000.00"),
            end_odometer=Decimal("14800.00"),
        )


@pytest.mark.django_db
def test_trip_distance_calculation(org_a, vehicle_a, driver_a):
    trip = Trip.objects.create(
        organization=org_a,
        vehicle=vehicle_a,
        driver=driver_a,
        status=TripStatus.COMPLETED,
        start_odometer=Decimal("12000.00"),
        end_odometer=Decimal("12450.00"),
        route_name="Depot to Site",
    )

    assert trip.distance_km == Decimal("450.00")
    assert trip.route_name == "Depot to Site"
