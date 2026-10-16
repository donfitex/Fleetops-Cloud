"""Helpers for scoping queries to the signed-in user's organizations."""

from apps.organizations.models import Membership


def user_organization_ids(user):
    if not user or not user.is_authenticated:
        return []
    return list(
        Membership.objects.filter(user=user, is_active=True).values_list(
            "organization_id",
            flat=True,
        )
    )


def scoped_queryset(queryset, user):
    organization_ids = user_organization_ids(user)
    if not organization_ids:
        return queryset.none()
    return queryset.filter(organization_id__in=organization_ids)
