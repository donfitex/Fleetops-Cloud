"""Template context for the authenticated app shell."""

from apps.organizations.models import Membership


def fleetops_shell(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {
            "user_memberships": [],
            "current_organization": None,
        }

    memberships = list(
        Membership.objects.filter(user=user, is_active=True)
        .select_related("organization")
        .order_by("organization__name")
    )
    current = memberships[0].organization if memberships else None
    return {
        "user_memberships": memberships,
        "current_organization": current,
    }
