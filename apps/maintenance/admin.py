from django.contrib import admin

from .models import MaintenanceSchedule, WorkOrder


@admin.register(MaintenanceSchedule)
class MaintenanceScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "vehicle",
        "maintenance_type",
        "interval_days",
        "interval_km",
        "next_due_date",
        "is_active",
        "organization",
    )
    list_filter = ("maintenance_type", "is_active", "organization")
    search_fields = ("title", "vehicle__registration_number")
    autocomplete_fields = ["organization", "vehicle"]


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "vehicle",
        "maintenance_type",
        "status",
        "priority",
        "service_cost",
        "scheduled_date",
        "completed_at",
        "organization",
    )
    list_filter = ("status", "priority", "maintenance_type", "organization")
    search_fields = ("title", "vehicle__registration_number", "vendor_name")
    autocomplete_fields = ["organization", "vehicle", "schedule"]
