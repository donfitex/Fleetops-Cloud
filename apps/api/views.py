from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.api.permissions import OrganizationRolePermission
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
from apps.assignments.models import VehicleAssignment
from apps.documents.models import AuditTrail, FleetDocument
from apps.drivers.models import Driver
from apps.expenses.models import Expense
from apps.fleet.models import Vehicle
from apps.maintenance.models import MaintenanceSchedule, WorkOrder
from apps.operations.models import FuelLog, Trip
from apps.organizations.models import Membership, Organization


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email") or request.data.get("username")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"detail": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, email=email, password=password)
    if user is None:
        return Response(
            {"detail": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {
            "token": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, OrganizationRolePermission])
def dashboard_summary(request):
    organization_ids = list(
        Membership.objects.filter(user=request.user, is_active=True).values_list(
            "organization_id", flat=True
        )
    )

    if not organization_ids:
        return Response(
            {
                "organizations": [],
                "totals": {
                    "vehicles": 0,
                    "drivers": 0,
                    "active_assignments": 0,
                    "open_work_orders": 0,
                    "monthly_expense_total": 0.0,
                },
            },
            status=status.HTTP_200_OK,
        )

    organizations = Organization.objects.filter(id__in=organization_ids)
    summary = []
    total_vehicles = 0
    total_drivers = 0
    total_active_assignments = 0
    total_open_work_orders = 0
    total_monthly_expenses = 0.0

    for organization in organizations:
        vehicles = Vehicle.objects.filter(organization=organization)
        drivers = Driver.objects.filter(organization=organization)
        active_assignments = VehicleAssignment.objects.filter(
            organization=organization,
            status="ACTIVE",
        )
        open_work_orders = WorkOrder.objects.filter(
            organization=organization,
        ).exclude(status__in=["COMPLETED", "CANCELLED"])
        monthly_total = Expense.objects.filter(
            organization=organization,
        ).aggregate(total=Sum("amount"))["total"] or 0

        organization_summary = {
            "organization_id": organization.id,
            "organization_name": organization.name,
            "vehicle_count": vehicles.count(),
            "driver_count": drivers.count(),
            "active_assignment_count": active_assignments.count(),
            "open_work_order_count": open_work_orders.count(),
            "monthly_expense_total": float(monthly_total),
        }
        summary.append(organization_summary)

        total_vehicles += organization_summary["vehicle_count"]
        total_drivers += organization_summary["driver_count"]
        total_active_assignments += organization_summary["active_assignment_count"]
        total_open_work_orders += organization_summary["open_work_order_count"]
        total_monthly_expenses += organization_summary["monthly_expense_total"]

    return Response(
        {
            "organizations": summary,
            "totals": {
                "vehicles": total_vehicles,
                "drivers": total_drivers,
                "active_assignments": total_active_assignments,
                "open_work_orders": total_open_work_orders,
                "monthly_expense_total": float(total_monthly_expenses),
            },
        },
        status=status.HTTP_200_OK,
    )


@login_required
def dashboard_page(request):
    organization_ids = list(
        Membership.objects.filter(user=request.user, is_active=True).values_list(
            "organization_id", flat=True
        )
    )
    organizations = Organization.objects.filter(id__in=organization_ids)

    dashboard_rows = []
    total_vehicles = 0
    total_drivers = 0
    total_active_assignments = 0
    total_open_work_orders = 0
    total_monthly_expenses = 0.0

    for organization in organizations:
        vehicles = Vehicle.objects.filter(organization=organization)
        drivers = Driver.objects.filter(organization=organization)
        active_assignments = VehicleAssignment.objects.filter(
            organization=organization,
            status="ACTIVE",
        )
        open_work_orders = WorkOrder.objects.filter(
            organization=organization,
        ).exclude(status__in=["COMPLETED", "CANCELLED"])
        monthly_total = Expense.objects.filter(
            organization=organization,
        ).aggregate(total=Sum("amount"))["total"] or 0

        row = {
            "organization_name": organization.name,
            "vehicle_count": vehicles.count(),
            "driver_count": drivers.count(),
            "active_assignment_count": active_assignments.count(),
            "open_work_order_count": open_work_orders.count(),
            "monthly_expense_total": float(monthly_total),
        }
        dashboard_rows.append(row)

        total_vehicles += row["vehicle_count"]
        total_drivers += row["driver_count"]
        total_active_assignments += row["active_assignment_count"]
        total_open_work_orders += row["open_work_order_count"]
        total_monthly_expenses += row["monthly_expense_total"]

    return render(
        request,
        "dashboard.html",
        {
            "organizations": dashboard_rows,
            "total_vehicles": total_vehicles,
            "total_drivers": total_drivers,
            "total_active_assignments": total_active_assignments,
            "total_open_work_orders": total_open_work_orders,
            "total_monthly_expenses": total_monthly_expenses,
        },
    )


class TenantScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, OrganizationRolePermission]

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
