from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet, BaseFilterSet

from netbox_data_flows import models

from .filters import *


__all__ = (
    "ObjectAliasTargetFilterSet",
    "ObjectAliasFilterSet",
)


class ObjectAliasTargetFilterSet(BaseFilterSet):
    class Meta:
        model = models.ObjectAliasTarget
        fields = ("id",)

    def search(self, queryset, name, value):
        return queryset


class ObjectAliasFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = models.ObjectAlias
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
