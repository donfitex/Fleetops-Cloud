"""
Management command to seed test demonstration data into FleetOps Cloud.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.assignments.models import AssignmentStatus, VehicleAssignment
from apps.drivers.models import Driver, DriverStatus
from apps.expenses.models import Expense, ExpenseCategory
from apps.fleet.models import FuelType, Vehicle, VehicleStatus
from apps.maintenance.models import (
    MaintenanceSchedule,
    MaintenanceStatus,
    MaintenanceType,
    WorkOrder,
    WorkOrderPriority,
)
from apps.operations.models import FuelLog, Trip, TripStatus
from apps.organizations.models import Membership, Organization, OrganizationRole


class Command(BaseCommand):
    help = "Populate database with demo organization, fleet, drivers, and operational records."

    def handle(self, *args, **options):
        self.stdout.write("Seeding FleetOps Cloud demo data...")

        # 1. Superuser / Admin
        admin_user, created = User.objects.get_or_create(
            email="admin@fleetops.com",
            defaults={
                "first_name": "System",
                "last_name": "Admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("Admin1234!")
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS("Created admin user: admin@fleetops.com / Admin1234!")
            )

        # 2. Regular User (Fleet Manager)
        manager_user, created = User.objects.get_or_create(
            email="manager@acmelogistics.com",
            defaults={
                "first_name": "Alex",
                "last_name": "Rivera",
            },
        )
        if created:
            manager_user.set_password("Manager1234!")
            manager_user.save()
            self.stdout.write(
                self.style.SUCCESS("Created manager user: manager@acmelogistics.com / Manager1234!")
            )

        # 3. Organization
        org, _ = Organization.objects.get_or_create(
            name="Acme Logistics Ltd",
            defaults={
                "contact_email": "operations@acmelogistics.com",
                "phone_number": "+44 20 7946 0912",
            },
        )

        # 4. Memberships
        Membership.objects.get_or_create(
            user=admin_user,
            organization=org,
            defaults={"role": OrganizationRole.OWNER},
        )
        Membership.objects.get_or_create(
            user=manager_user,
            organization=org,
            defaults={"role": OrganizationRole.FLEET_MANAGER},
        )

        # 5. Vehicles
        v1, _ = Vehicle.objects.get_or_create(
            organization=org,
            registration_number="FL24-OPS",
            defaults={
                "make": "Ford",
                "model": "Transit Custom",
                "year": 2024,
                "fuel_type": FuelType.DIESEL,
                "status": VehicleStatus.ACTIVE,
                "current_odometer": Decimal("14250.00"),
            },
        )
        v2, _ = Vehicle.objects.get_or_create(
            organization=org,
            registration_number="EV23-TRK",
            defaults={
                "make": "Mercedes-Benz",
                "model": "eVito",
                "year": 2023,
                "fuel_type": FuelType.ELECTRIC,
                "status": VehicleStatus.ACTIVE,
                "current_odometer": Decimal("8300.00"),
            },
        )
        v3, _ = Vehicle.objects.get_or_create(
            organization=org,
            registration_number="HD21-VOL",
            defaults={
                "make": "Volvo",
                "model": "FH16 Heavy Truck",
                "year": 2021,
                "fuel_type": FuelType.DIESEL,
                "status": VehicleStatus.MAINTENANCE,
                "current_odometer": Decimal("92100.00"),
            },
        )

        # 6. Drivers
        d1, _ = Driver.objects.get_or_create(
            organization=org,
            license_number="RIV991204AB",
            defaults={
                "first_name": "Marcus",
                "last_name": "Vance",
                "phone_number": "+44 7700 900111",
                "status": DriverStatus.ACTIVE,
                "license_class": "Class C Commercial",
            },
        )
        d2, _ = Driver.objects.get_or_create(
            organization=org,
            license_number="JON880115CD",
            defaults={
                "first_name": "Sarah",
                "last_name": "Jenkins",
                "phone_number": "+44 7700 900222",
                "status": DriverStatus.ACTIVE,
                "license_class": "Class B",
            },
        )

        # 7. Assignment
        VehicleAssignment.objects.get_or_create(
            organization=org,
            vehicle=v1,
            driver=d1,
            status=AssignmentStatus.ACTIVE,
            defaults={"notes": "Daily regional deliveries."},
        )

        # 8. Maintenance Schedule & Work Order
        MaintenanceSchedule.objects.get_or_create(
            organization=org,
            vehicle=v1,
            title="15,000 km Oil & Filter Service",
            defaults={
                "maintenance_type": MaintenanceType.OIL_CHANGE,
                "interval_km": Decimal("15000.00"),
                "interval_days": 180,
            },
        )
        WorkOrder.objects.get_or_create(
            organization=org,
            vehicle=v3,
            title="Brake Pad Replacement & Inspection",
            defaults={
                "maintenance_type": MaintenanceType.BRAKE_SERVICE,
                "service_cost": Decimal("485.50"),
                "status": MaintenanceStatus.IN_PROGRESS,
                "priority": WorkOrderPriority.HIGH,
                "vendor_name": "Apex Commercial Garage",
            },
        )

        # 9. Operations (Fuel & Trips)
        FuelLog.objects.get_or_create(
            organization=org,
            vehicle=v1,
            refilled_at=timezone.now(),
            defaults={
                "quantity": Decimal("65.00"),
                "unit_cost": Decimal("1.45"),
                "total_cost": Decimal("94.25"),
                "odometer_reading": Decimal("14200.00"),
            },
        )
        Trip.objects.get_or_create(
            organization=org,
            vehicle=v1,
            driver=d1,
            start_time=timezone.now() - timezone.timedelta(hours=4),
            defaults={
                "end_time": timezone.now() - timezone.timedelta(hours=1),
                "start_odometer": Decimal("14100.00"),
                "end_odometer": Decimal("14250.00"),
                "status": TripStatus.COMPLETED,
            },
        )

        # 10. Expenses
        Expense.objects.get_or_create(
            organization=org,
            vehicle=v1,
            title="M6 Toll passage fee",
            category=ExpenseCategory.TOLLS,
            defaults={
                "amount": Decimal("14.50"),
                "occurred_on": timezone.now().date(),
                "notes": "Route delivery fee",
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo database successfully populated!"))
