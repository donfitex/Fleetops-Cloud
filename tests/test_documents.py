import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.documents.models import AuditTrail, DocumentCategory, FleetDocument
from apps.drivers.models import Driver
from apps.fleet.models import Vehicle
from apps.organizations.models import Organization


@pytest.fixture
def org_a(db):
    return Organization.objects.create(name="Document Group A")


@pytest.fixture
def org_b(db):
    return Organization.objects.create(name="Document Group B")


@pytest.fixture
def vehicle_a(db, org_a):
    return Vehicle.objects.create(
        organization=org_a,
        registration_number="DOC-101",
        make="Toyota",
        model="Hiace",
        year=2023,
    )


@pytest.fixture
def vehicle_b(db, org_b):
    return Vehicle.objects.create(
        organization=org_b,
        registration_number="DOC-202",
        make="Citroen",
        model="Jumpy",
        year=2024,
    )


@pytest.fixture
def driver_a(db, org_a):
    return Driver.objects.create(
        organization=org_a,
        first_name="Harper",
        last_name="Ross",
        license_number="DOC-DRIVER-1",
        phone_number="+44 7700 900555",
    )


@pytest.fixture
def driver_b(db, org_b):
    return Driver.objects.create(
        organization=org_b,
        first_name="Jordan",
        last_name="Cruz",
        license_number="DOC-DRIVER-2",
        phone_number="+44 7700 900666",
    )


@pytest.fixture
def user_a(db):
    return User.objects.create_user(
        email="auditor@fleetops.test",
        password="StrongPassword123!",
        first_name="Auditor",
        last_name="One",
    )


@pytest.mark.django_db
def test_document_creation_and_tenant_scoping(org_a, vehicle_a, driver_a):
    document = FleetDocument.objects.create(
        organization=org_a,
        vehicle=vehicle_a,
        driver=driver_a,
        category=DocumentCategory.REGISTRATION,
        title="Vehicle registration",
        file_name="registration.pdf",
        file_size=2048,
        mime_type="application/pdf",
        storage_path="/documents/registration.pdf",
    )

    assert document.organization == org_a
    assert document.vehicle == vehicle_a
    assert document.driver == driver_a
    assert document.status == "UPLOADED"


@pytest.mark.django_db
def test_document_rejects_cross_tenant_vehicle(org_a, org_b, vehicle_b, driver_a):
    with pytest.raises(ValidationError):
        FleetDocument.objects.create(
            organization=org_a,
            vehicle=vehicle_b,
            driver=driver_a,
            category=DocumentCategory.DRIVER,
            title="Wrong tenant document",
            file_name="wrong.pdf",
            storage_path="/documents/wrong.pdf",
        )


@pytest.mark.django_db
def test_audit_trail_is_recorded_for_entity(org_a, user_a):
    audit = AuditTrail.objects.create(
        organization=org_a,
        entity_type="Vehicle",
        entity_id=101,
        action="UPDATED",
        actor=user_a,
        details="Status changed to active",
    )

    assert audit.organization == org_a
    assert audit.action == "UPDATED"
    assert audit.actor == user_a
    assert "Status changed" in audit.details
