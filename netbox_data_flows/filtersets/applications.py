from django.db.models import Q

from netbox.filtersets import OrganizationalModelFilterSet, PrimaryModelFilterSet
from utilities.filtersets import register_filterset

from tenancy.filtersets import ContactModelFilterSet, TenancyFilterSet

from netbox_data_flows import models

from .filters import ModelMultipleChoiceFilter


__all__ = (
    "ApplicationFilterSet",
    "ApplicationRoleFilterSet",
)


@register_filterset
class ApplicationRoleFilterSet(OrganizationalModelFilterSet):
    class Meta:
        model = models.ApplicationRole
        fields = (
            "id",
            "name",
            "slug",
            "description",
        )


@register_filterset
class ApplicationFilterSet(ContactModelFilterSet, TenancyFilterSet, PrimaryModelFilterSet):
    role_id = ModelMultipleChoiceFilter(
        queryset=models.ApplicationRole.objects.all(),
        label="Application Role (ID)",
    )
    role = ModelMultipleChoiceFilter(
        field_name="role__slug",
        queryset=models.ApplicationRole.objects.all(),
        to_field_name="slug",
        label="Application Role (Slug)",
    )

    class Meta:
        model = models.Application
        fields = (
            "id",
            "name",
            "description",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset

        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)
