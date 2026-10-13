from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.organizations.models import OrganizationRole


class OrganizationRolePermission(BasePermission):
    """Allow read access to any active organization member and write access to managers."""

    message = "You do not have the required role to perform this action within the organization."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        active_memberships = request.user.memberships.filter(is_active=True)
        if request.method in SAFE_METHODS:
            return active_memberships.exists()

        return active_memberships.filter(
            role__in=[
                OrganizationRole.OWNER,
                OrganizationRole.ADMIN,
                OrganizationRole.FLEET_MANAGER,
            ]
        ).exists()
