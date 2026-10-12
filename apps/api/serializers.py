from rest_framework import serializers

from apps.assignments.models import VehicleAssignment
from apps.drivers.models import Driver
from apps.documents.models import AuditTrail, FleetDocument
from apps.expenses.models import Expense
from apps.fleet.models import Vehicle
from apps.maintenance.models import MaintenanceSchedule, WorkOrder
from apps.operations.models import FuelLog, Trip
from apps.organizations.models import Membership, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "slug", "contact_email", "phone_number", "is_active"]
        read_only_fields = fields


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ["id", "organization", "role", "is_active"]
        read_only_fields = ["id", "organization"]


class VehicleSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "organization",
            "registration_number",
            "vin",
            "make",
            "model",
            "year",
            "status",
            "fuel_type",
            "current_odometer",
        ]
        read_only_fields = ["id", "organization"]


class DriverSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Driver
        fields = [
            "id",
            "organization",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "license_number",
            "license_class",
            "license_expiry_date",
            "status",
        ]
        read_only_fields = ["id", "organization"]


class VehicleAssignmentSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = VehicleAssignment
        fields = [
            "id",
            "organization",
            "vehicle",
            "driver",
            "start_time",
            "end_time",
            "status",
            "notes",
        ]
        read_only_fields = ["id", "organization"]


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MaintenanceSchedule
        fields = [
            "id",
            "organization",
            "vehicle",
            "title",
            "maintenance_type",
            "interval_days",
            "interval_km",
            "next_due_date",
            "next_due_odometer",
            "is_active",
            "notes",
        ]
        read_only_fields = ["id", "organization"]


class WorkOrderSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            "id",
            "organization",
            "vehicle",
            "schedule",
            "title",
            "maintenance_type",
            "status",
            "priority",
            "requested_at",
            "scheduled_date",
            "completed_at",
            "service_cost",
            "odometer_reading",
            "vendor_name",
            "notes",
        ]
        read_only_fields = ["id", "organization"]


class FuelLogSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FuelLog
        fields = [
            "id",
            "organization",
            "vehicle",
            "fuel_type",
            "quantity",
            "unit_cost",
            "total_cost",
            "odometer_reading",
            "refilled_at",
            "vendor_name",
            "notes",
        ]
        read_only_fields = ["id", "organization"]


class TripSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Trip
        fields = [
            "id",
            "organization",
            "vehicle",
            "driver",
            "status",
            "start_time",
            "end_time",
            "start_odometer",
            "end_odometer",
            "route_name",
            "notes",
        ]
        read_only_fields = ["id", "organization"]


class ExpenseSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "organization",
            "vehicle",
            "driver",
            "category",
            "title",
            "amount",
            "occurred_on",
            "vendor_name",
            "receipt_reference",
            "notes",
        ]
        read_only_fields = ["id", "organization"]


class FleetDocumentSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = FleetDocument
        fields = [
            "id",
            "organization",
            "vehicle",
            "driver",
            "category",
            "title",
            "file_name",
            "file_size",
            "mime_type",
            "storage_path",
            "status",
            "notes",
        ]
        read_only_fields = ["id", "organization"]


class AuditTrailSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)
    actor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AuditTrail
        fields = [
            "id",
            "organization",
            "entity_type",
            "entity_id",
            "action",
            "actor",
            "details",
            "created_at",
        ]
        read_only_fields = ["id", "organization", "actor", "created_at"]
