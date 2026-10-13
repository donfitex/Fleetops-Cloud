from django.contrib import admin

from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "amount",
        "occurred_on",
        "vehicle",
        "driver",
        "vendor_name",
        "organization",
    )
    list_filter = ("category", "organization", "occurred_on")
    search_fields = ("title", "vendor_name", "receipt_reference", "vehicle__registration_number")
    autocomplete_fields = ["organization", "vehicle", "driver"]
