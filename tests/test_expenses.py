import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.drivers.models import Driver
from apps.expenses.models import Expense, ExpenseCategory
from apps.fleet.models import Vehicle
from apps.organizations.models import Organization


@pytest.fixture
def org_a(db):
    return Organization.objects.create(name="FleetCare West")


@pytest.fixture
def org_b(db):
    return Organization.objects.create(name="FleetCare East")


@pytest.fixture
def vehicle_a(db, org_a):
    return Vehicle.objects.create(
        organization=org_a,
        registration_number="EXP-101",
        make="Peugeot",
        model="Boxer",
        year=2021,
    )


@pytest.fixture
def vehicle_b(db, org_b):
    return Vehicle.objects.create(
        organization=org_b,
        registration_number="EXP-202",
        make="Iveco",
        model="Daily",
        year=2022,
    )


@pytest.fixture
def driver_a(db, org_a):
    return Driver.objects.create(
        organization=org_a,
        first_name="Cora",
        last_name="Lane",
        license_number="CORA-220",
        phone_number="+44 7700 900333",
    )


@pytest.fixture
def driver_b(db, org_b):
    return Driver.objects.create(
        organization=org_b,
        first_name="Drew",
        last_name="Stone",
        license_number="DREW-440",
        phone_number="+44 7700 900444",
    )


@pytest.mark.django_db
def test_expense_creation_and_amount_validation(org_a, vehicle_a, driver_a):
    expense = Expense.objects.create(
        organization=org_a,
        vehicle=vehicle_a,
        driver=driver_a,
        category=ExpenseCategory.PARKING,
        title="City parking",
        amount=Decimal("18.50"),
        vendor_name="Metro Parking",
    )

    assert expense.amount == Decimal("18.50")
    assert expense.organization == org_a
    assert expense.vehicle == vehicle_a
    assert expense.driver == driver_a


@pytest.mark.django_db
def test_expense_rejects_cross_tenant_vehicle_or_driver(org_a, org_b, vehicle_a, vehicle_b, driver_a, driver_b):
    with pytest.raises(ValidationError):
        Expense.objects.create(
            organization=org_a,
            vehicle=vehicle_b,
            driver=driver_a,
            category=ExpenseCategory.TOLLS,
            title="Wrong vehicle tenant",
            amount=Decimal("12.00"),
        )

    with pytest.raises(ValidationError):
        Expense.objects.create(
            organization=org_a,
            vehicle=vehicle_a,
            driver=driver_b,
            category=ExpenseCategory.TOLLS,
            title="Wrong driver tenant",
            amount=Decimal("12.00"),
        )


@pytest.mark.django_db
def test_negative_expense_amount_is_rejected(org_a, vehicle_a):
    with pytest.raises(ValidationError):
        Expense.objects.create(
            organization=org_a,
            vehicle=vehicle_a,
            category=ExpenseCategory.OTHER,
            title="Refund or correction",
            amount=Decimal("-5.00"),
        )
