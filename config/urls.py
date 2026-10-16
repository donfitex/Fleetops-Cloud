"""
FleetOps Cloud — Root URL Configuration.
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.core import web as web_views

urlpatterns = [
    # Root → redirect to dashboard (which redirects to login if unauthenticated)
    path("", RedirectView.as_view(url="/dashboard/", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    # Auth: login, logout, password-reset (uses templates/registration/)
    path("accounts/", include("django.contrib.auth.urls")),
    # Main app
    path("dashboard/", web_views.dashboard_page, name="dashboard"),
    path("vehicles/", web_views.vehicle_list, name="vehicle-list"),
    path("drivers/", web_views.driver_list, name="driver-list"),
    path("assignments/", web_views.assignment_list, name="assignment-list"),
    path("maintenance/", web_views.maintenance_list, name="maintenance-list"),
    path("expenses/", web_views.expense_list, name="expense-list"),
    path("operations/", web_views.operations_list, name="operations-list"),
    path("documents/", web_views.document_list, name="document-list"),
    path("reports/", web_views.reports_page, name="reports"),
    path("reports/export/", web_views.reports_export, name="reports-export"),
    path("profile/", web_views.profile_page, name="profile"),
    path("api/v1/", include("apps.api.urls")),
    # OpenAPI Schema & Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
