from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.assignments.models import VehicleAssignment
from apps.drivers.models import Driver
from apps.documents.models import AuditTrail, FleetDocument
from apps.expenses.models import Expense
from apps.fleet.models import Vehicle
from apps.maintenance.models import MaintenanceSchedule, WorkOrder
from apps.operations.models import FuelLog, Trip
from apps.organizations.models import Membership, Organization
from apps.api.serializers import (
    AuditTrailSerializer,
    DriverSerializer,
    ExpenseSerializer,
    FleetDocumentSerializer,
    FuelLogSerializer,
    MaintenanceScheduleSerializer,
    MembershipSerializer,
    OrganizationSerializer,
    TripSerializer,
    VehicleAssignmentSerializer,
    VehicleSerializer,
    WorkOrderSerializer,
)


class TenantScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_user_organization_ids(self):
        return list(
            Membership.objects.filter(user=self.request.user, is_active=True).values_list(
                "organization_id", flat=True
            )
        )

    def get_queryset(self):
        organization_ids = self.get_user_organization_ids()
        if not organization_ids:
            return self.queryset.none()
        return self.queryset.filter(organization_id__in=organization_ids)

    def perform_create(self, serializer):
        organization_ids = self.get_user_organization_ids()
        if not organization_ids:
            raise PermissionError("User is not a member of any organization.")
        serializer.save(organization_id=organization_ids[0])


class OrganizationViewSet(TenantScopedViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        return Organization.objects.filter(
            id__in=self.get_user_organization_ids()
        )


class MembershipViewSet(TenantScopedViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer


class VehicleViewSet(TenantScopedViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


class DriverViewSet(TenantScopedViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


class VehicleAssignmentViewSet(TenantScopedViewSet):
    queryset = VehicleAssignment.objects.all()
    serializer_class = VehicleAssignmentSerializer


class MaintenanceScheduleViewSet(TenantScopedViewSet):
    queryset = MaintenanceSchedule.objects.all()
    serializer_class = MaintenanceScheduleSerializer


class WorkOrderViewSet(TenantScopedViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer


class FuelLogViewSet(TenantScopedViewSet):
    queryset = FuelLog.objects.all()
    serializer_class = FuelLogSerializer


class TripViewSet(TenantScopedViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class ExpenseViewSet(TenantScopedViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class FleetDocumentViewSet(TenantScopedViewSet):
    queryset = FleetDocument.objects.all()
    serializer_class = FleetDocumentSerializer


class AuditTrailViewSet(TenantScopedViewSet):
    queryset = AuditTrail.objects.all()
    serializer_class = AuditTrailSerializer
