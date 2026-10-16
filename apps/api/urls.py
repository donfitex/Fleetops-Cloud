from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.api.views import (
    AuditTrailViewSet,
    DriverViewSet,
    ExpenseViewSet,
    FleetDocumentViewSet,
    FuelLogViewSet,
    MaintenanceScheduleViewSet,
    MembershipViewSet,
    NotificationViewSet,
    OrganizationViewSet,
    TripViewSet,
    VehicleAssignmentViewSet,
    VehicleViewSet,
    WorkOrderViewSet,
    dashboard_summary,
    login_user,
)

router = DefaultRouter()
router.register(r"organizations", OrganizationViewSet, basename="organizations")
router.register(r"memberships", MembershipViewSet, basename="memberships")
router.register(r"vehicles", VehicleViewSet, basename="vehicles")
router.register(r"drivers", DriverViewSet, basename="drivers")
router.register(r"assignments", VehicleAssignmentViewSet, basename="assignments")
router.register(
    r"maintenance-schedules", MaintenanceScheduleViewSet, basename="maintenance-schedules"
)
router.register(r"work-orders", WorkOrderViewSet, basename="work-orders")
router.register(r"fuel-logs", FuelLogViewSet, basename="fuel-logs")
router.register(r"trips", TripViewSet, basename="trips")
router.register(r"expenses", ExpenseViewSet, basename="expenses")
router.register(r"documents", FleetDocumentViewSet, basename="documents")
router.register(r"audit-trails", AuditTrailViewSet, basename="audit-trails")
router.register(r"notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("auth/login/", login_user, name="api-login"),
    path("dashboard/summary/", dashboard_summary, name="dashboard-summary"),
    path("", include(router.urls)),
]
