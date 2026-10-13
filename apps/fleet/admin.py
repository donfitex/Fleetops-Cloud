from django.contrib import admin

from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "registration_number",
        "make",
        "model",
        "year",
        "fuel_type",
        "status",
        "current_odometer",
        "organization",
    )
    list_filter = ("status", "fuel_type", "organization", "year")
    search_fields = ("registration_number", "vin", "make", "model")
    autocomplete_fields = ["organization"]
