from django.contrib import admin

from .models import VehicleAssignment


@admin.register(VehicleAssignment)
class VehicleAssignmentAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "driver", "status", "start_time", "end_time", "organization")
    list_filter = ("status", "organization", "start_time")
    search_fields = (
        "vehicle__registration_number",
        "driver__first_name",
        "driver__last_name",
        "driver__license_number",
    )
    autocomplete_fields = ["organization", "vehicle", "driver"]
