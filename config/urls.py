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

from apps.api.views import dashboard_page

urlpatterns = [
    # Root → redirect to dashboard (which redirects to login if unauthenticated)
    path("", RedirectView.as_view(url="/dashboard/", permanent=False), name="home"),
    path("admin/", admin.site.urls),
    # Auth: login, logout, password-reset (uses templates/registration/)
    path("accounts/", include("django.contrib.auth.urls")),
    # Main app
    path("dashboard/", dashboard_page, name="dashboard"),
    path("api/v1/", include("apps.api.urls")),
    # OpenAPI Schema & Docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
