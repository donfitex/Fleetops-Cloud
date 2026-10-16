"""Tenant-scoped HTML views for the FleetOps Cloud app shell."""

import csv
import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from apps.assignments.models import VehicleAssignment
from apps.core.tenancy import scoped_queryset, user_organization_ids
from apps.documents.models import FleetDocument
from apps.drivers.models import Driver
from apps.expenses.models import Expense
from apps.fleet.models import Vehicle, VehicleStatus
from apps.maintenance.models import MaintenanceSchedule, MaintenanceStatus, WorkOrder
from apps.operations.models import FuelLog, Trip
from apps.organizations.models import Organization


def _local_today():
    return timezone.localdate()


@login_required
def dashboard_page(request):
    organization_ids = user_organization_ids(request.user)
    organizations = Organization.objects.filter(id__in=organization_ids)
    today = _local_today()
    soon = today + timedelta(days=30)
    week = today + timedelta(days=7)

    vehicles = Vehicle.objects.filter(organization_id__in=organization_ids)
    drivers = Driver.objects.filter(organization_id__in=organization_ids)
    assignments = VehicleAssignment.objects.filter(organization_id__in=organization_ids)
    work_orders = WorkOrder.objects.filter(organization_id__in=organization_ids)
    expenses = Expense.objects.filter(organization_id__in=organization_ids)
    schedules = MaintenanceSchedule.objects.filter(
        organization_id__in=organization_ids,
        is_active=True,
    )

    total_vehicles = vehicles.count()
    total_drivers = drivers.count()
    total_active_assignments = assignments.filter(status="ACTIVE").count()
    open_work_orders = work_orders.exclude(
        status__in=[MaintenanceStatus.COMPLETED, MaintenanceStatus.CANCELLED]
    )
    total_open_work_orders = open_work_orders.count()
    total_monthly_expenses = expenses.filter(
        occurred_on__gte=today.replace(day=1)
    ).aggregate(total=Sum("amount"))["total"] or 0

    active_vehicles = vehicles.filter(status=VehicleStatus.ACTIVE).count()
    fleet_health = round((active_vehicles / total_vehicles) * 100) if total_vehicles else 0

    dashboard_rows = []
    for organization in organizations:
        org_vehicles = vehicles.filter(organization=organization)
        org_drivers = drivers.filter(organization=organization)
        dashboard_rows.append(
            {
                "organization_name": organization.name,
                "vehicle_count": org_vehicles.count(),
                "driver_count": org_drivers.count(),
                "active_assignment_count": assignments.filter(
                    organization=organization,
                    status="ACTIVE",
                ).count(),
                "open_work_order_count": open_work_orders.filter(
                    organization=organization
                ).count(),
                "monthly_expense_total": float(
                    expenses.filter(
                        organization=organization,
                        occurred_on__gte=today.replace(day=1),
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
                ),
            }
        )

    status_counts = {
        choice.value: 0 for choice in VehicleStatus
    }
    for row in vehicles.values("status").annotate(total=Count("id")):
        status_counts[row["status"]] = row["total"]

    work_order_counts = {
        "Open": open_work_orders.exclude(status=MaintenanceStatus.IN_PROGRESS).count(),
        "In progress": open_work_orders.filter(status=MaintenanceStatus.IN_PROGRESS).count(),
        "Completed": work_orders.filter(status=MaintenanceStatus.COMPLETED).count(),
    }

    alerts = []
    for order in (
        open_work_orders.filter(priority__in=["HIGH", "CRITICAL"])
        .select_related("vehicle")
        .order_by("-requested_at")[:5]
    ):
        alerts.append(
            {
                "title": order.title,
                "detail": f"{order.vehicle.registration_number} · {order.get_priority_display()}",
                "tone": "red" if order.priority == "CRITICAL" else "amber",
                "badge": order.get_priority_display(),
            }
        )

    overdue_schedules = schedules.filter(next_due_date__lt=today).select_related("vehicle")[:5]
    for schedule in overdue_schedules:
        alerts.append(
            {
                "title": f"Overdue: {schedule.title}",
                "detail": f"{schedule.vehicle.registration_number} · due {schedule.next_due_date}",
                "tone": "red",
                "badge": "Overdue",
            }
        )

    expiring_licenses = drivers.filter(
        license_expiry_date__isnull=False,
        license_expiry_date__lte=soon,
    ).order_by("license_expiry_date")
    for driver in expiring_licenses[:5]:
        alerts.append(
            {
                "title": f"License expiring · {driver.full_name}",
                "detail": f"{driver.license_number} · {driver.license_expiry_date}",
                "tone": "sky",
                "badge": "License",
            }
        )

    context = {
        "organizations": dashboard_rows,
        "total_vehicles": total_vehicles,
        "total_drivers": total_drivers,
        "total_active_assignments": total_active_assignments,
        "total_open_work_orders": total_open_work_orders,
        "total_monthly_expenses": total_monthly_expenses,
        "fleet_health": fleet_health,
        "maintenance_due_count": schedules.filter(next_due_date__lte=week).count(),
        "expiring_license_count": expiring_licenses.count(),
        "status_breakdown": json.dumps(
            [{"label": label.replace("_", " ").title(), "value": value} for label, value in status_counts.items()]
        ),
        "work_order_breakdown": json.dumps(
            [{"label": label, "value": value} for label, value in work_order_counts.items()]
        ),
        "alerts": alerts[:8],
        "recent_assignments": assignments.select_related("vehicle", "driver").order_by("-start_time")[:6],
        "recent_work_orders": work_orders.select_related("vehicle").order_by("-requested_at")[:6],
        "recent_expenses": expenses.select_related("vehicle").order_by("-occurred_on", "-created_at")[:6],
        "upcoming_maintenance": schedules.filter(next_due_date__lte=week)
        .select_related("vehicle")
        .order_by("next_due_date")[:6],
    }
    return render(request, "dashboard.html", context)


@login_required
def vehicle_list(request):
    status_filter = request.GET.get("status", "")
    vehicles = scoped_queryset(Vehicle.objects.all(), request.user).select_related("organization")
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    return render(
        request,
        "pages/vehicles.html",
        {
            "vehicles": vehicles,
            "status_filter": status_filter,
            "status_choices": VehicleStatus.choices,
        },
    )


@login_required
def driver_list(request):
    drivers = scoped_queryset(Driver.objects.all(), request.user).select_related("organization")
    return render(request, "pages/drivers.html", {"drivers": drivers})


@login_required
def assignment_list(request):
    assignments = scoped_queryset(VehicleAssignment.objects.all(), request.user).select_related(
        "vehicle",
        "driver",
        "organization",
    )
    return render(request, "pages/assignments.html", {"assignments": assignments})


@login_required
def maintenance_list(request):
    org_ids = user_organization_ids(request.user)
    work_orders = WorkOrder.objects.filter(organization_id__in=org_ids).select_related(
        "vehicle",
        "organization",
    )
    schedules = MaintenanceSchedule.objects.filter(
        organization_id__in=org_ids,
        is_active=True,
    ).select_related("vehicle")
    return render(
        request,
        "pages/maintenance.html",
        {
            "work_orders": work_orders,
            "schedules": schedules,
        },
    )


@login_required
def expense_list(request):
    expenses = scoped_queryset(Expense.objects.all(), request.user).select_related(
        "vehicle",
        "driver",
        "organization",
    )
    total = expenses.aggregate(total=Sum("amount"))["total"] or 0
    return render(request, "pages/expenses.html", {"expenses": expenses, "expense_total": total})


@login_required
def operations_list(request):
    org_ids = user_organization_ids(request.user)
    trips = Trip.objects.filter(organization_id__in=org_ids).select_related("vehicle", "driver")
    fuel_logs = FuelLog.objects.filter(organization_id__in=org_ids).select_related("vehicle")
    return render(
        request,
        "pages/operations.html",
        {
            "trips": trips,
            "fuel_logs": fuel_logs,
        },
    )


@login_required
def document_list(request):
    documents = scoped_queryset(FleetDocument.objects.all(), request.user).select_related(
        "vehicle",
        "driver",
        "organization",
    )
    return render(request, "pages/documents.html", {"documents": documents})


@login_required
def reports_page(request):
    org_ids = user_organization_ids(request.user)
    today = _local_today()
    month_start = today.replace(day=1)

    vehicles = Vehicle.objects.filter(organization_id__in=org_ids)
    expenses = Expense.objects.filter(organization_id__in=org_ids)
    work_orders = WorkOrder.objects.filter(organization_id__in=org_ids)

    category_spend = list(
        expenses.filter(occurred_on__gte=month_start)
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    status_counts = list(vehicles.values("status").annotate(total=Count("id")).order_by("status"))

    return render(
        request,
        "pages/reports.html",
        {
            "vehicle_count": vehicles.count(),
            "open_work_orders": work_orders.exclude(
                status__in=[MaintenanceStatus.COMPLETED, MaintenanceStatus.CANCELLED]
            ).count(),
            "month_spend": expenses.filter(occurred_on__gte=month_start).aggregate(total=Sum("amount"))["total"]
            or 0,
            "completed_trips": Trip.objects.filter(organization_id__in=org_ids, status="COMPLETED").count(),
            "category_spend": category_spend,
            "status_counts": status_counts,
            "category_chart": json.dumps(
                [
                    {"label": row["category"].replace("_", " ").title(), "value": float(row["total"] or 0)}
                    for row in category_spend
                ]
            ),
            "status_chart": json.dumps(
                [
                    {"label": row["status"].replace("_", " ").title(), "value": row["total"]}
                    for row in status_counts
                ]
            ),
        },
    )


@login_required
def reports_export(request):
    expenses = scoped_queryset(Expense.objects.all(), request.user).select_related("vehicle", "organization")
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="fleetops-expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(["Date", "Organization", "Title", "Category", "Vehicle", "Amount"])
    for expense in expenses:
        writer.writerow(
            [
                expense.occurred_on.isoformat(),
                expense.organization.name,
                expense.title,
                expense.category,
                expense.vehicle.registration_number if expense.vehicle_id else "",
                f"{expense.amount:.2f}",
            ]
        )
    return response


@login_required
def profile_page(request):
    return render(request, "pages/profile.html")
