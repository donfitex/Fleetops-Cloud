from django.contrib import admin

from .models import Driver


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "license_number",
        "license_class",
        "license_expiry_date",
        "status",
        "phone_number",
        "organization",
    )
    list_filter = ("status", "organization", "license_class")
    search_fields = ("first_name", "last_name", "license_number", "phone_number")
    autocomplete_fields = ["organization", "user"]
