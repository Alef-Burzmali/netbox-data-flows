from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from netbox_data_flows.models import (
    ObjectAlias,
    ObjectAliasTarget,
)

from .filters import ModelMultipleChoiceFilter


__all__ = ("ObjectAliasFilterSet",)


class ObjectAliasFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = ObjectAlias
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
