from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet, OrganizationalModelFilterSet

from tenancy.filtersets import ContactModelFilterSet, TenancyFilterSet

from netbox_data_flows import models

from .filters import ModelMultipleChoiceFilter


__all__ = (
    "ApplicationFilterSet",
    "ApplicationRoleFilterSet",
)


class ApplicationRoleFilterSet(OrganizationalModelFilterSet):
    class Meta:
        model = models.ApplicationRole
        fields = (
            "id",
            "name",
            "slug",
            "description",
        )


class ApplicationFilterSet(ContactModelFilterSet, TenancyFilterSet, NetBoxModelFilterSet):
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
            "role",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset

        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)
