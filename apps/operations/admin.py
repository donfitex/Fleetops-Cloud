from django.contrib import admin

from .models import FuelLog, Trip


@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "quantity",
        "unit_cost",
        "total_cost",
        "odometer_reading",
        "fuel_type",
        "refilled_at",
        "organization",
    )
    list_filter = ("fuel_type", "organization", "refilled_at")
    search_fields = ("vehicle__registration_number", "vendor_name")
    autocomplete_fields = ["organization", "vehicle"]


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "vehicle",
        "driver",
        "status",
        "start_time",
        "end_time",
        "start_odometer",
        "end_odometer",
        "distance_km",
        "organization",
    )
    list_filter = ("status", "organization", "start_time")
    search_fields = (
        "vehicle__registration_number",
        "driver__first_name",
        "driver__last_name",
        "route_name",
    )
    autocomplete_fields = ["organization", "vehicle", "driver"]
