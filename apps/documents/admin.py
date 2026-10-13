from django.contrib import admin

from .models import AuditTrail, FleetDocument


@admin.register(FleetDocument)
class FleetDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "vehicle",
        "driver",
        "status",
        "created_at",
        "organization",
    )
    list_filter = ("category", "status", "organization")
    search_fields = (
        "title",
        "vehicle__registration_number",
        "driver__first_name",
        "driver__last_name",
    )
    autocomplete_fields = ["organization", "vehicle", "driver"]


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "entity_type",
        "entity_id",
        "actor",
        "created_at",
        "organization",
    )
    list_filter = ("action", "entity_type", "organization", "created_at")
    search_fields = ("action", "entity_type", "actor__email", "details")
    autocomplete_fields = ["organization", "actor"]
    readonly_fields = (
        "action",
        "entity_type",
        "entity_id",
        "actor",
        "details",
        "created_at",
    )
