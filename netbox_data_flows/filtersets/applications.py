from netbox.filtersets import NetBoxModelFilterSet

from netbox_data_flows.models import (
    Application,
    ApplicationRole,
)

from .filters import ModelMultipleChoiceFilter


__all__ = (
    "ApplicationFilterSet",
    "ApplicationRoleFilterSet",
)


class ApplicationRoleFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ApplicationRole
        fields = (
            "id",
            "name",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset

        return queryset.filter(name__icontains=value)


class ApplicationFilterSet(NetBoxModelFilterSet):
    role_id = ModelMultipleChoiceFilter(
        queryset=ApplicationRole.objects.all(),
        label="Application Role (ID)",
    )
    role = ModelMultipleChoiceFilter(
        queryset=ApplicationRole.objects.all(),
        label="Application Role (Name)",
    )

    class Meta:
        model = Application
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
