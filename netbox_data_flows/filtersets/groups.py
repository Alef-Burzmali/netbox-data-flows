from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from netbox_data_flows import models

from .addins import *
from .filters import *

__all__ = ("DataFlowGroupFilterSet",)


class DataFlowGroupFilterSet(
    ApplicationFilterSetAddin,
    InheritedStatusFilterSetAddin,
    NetBoxModelFilterSet,
):
    parent_id = TreeNodeMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        lookup_expr="in",
        label="Parent (ID)",
    )
    parent = TreeNodeMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        lookup_expr="in",
        to_field_name="name",
        label="Parent (name)",
    )
    ancestor_id = TreeNodeMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        label="Ancestor (ID)",
        method="filter_ancestors",
    )
    ancestor = TreeNodeMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        to_field_name="name",
        label="Ancestor (name)",
        method="filter_ancestors",
    )

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "id",
            "name",
            "status",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset

        qs_filter = Q(name__icontains=value) | Q(description__icontains=value)
        return queryset.filter(qs_filter)

    def filter_ancestors(self, queryset, name, value):
        if not value:
            return queryset

        descendants = (
            models.DataFlowGroup.objects.filter(pk__in=value)
            .get_descendants(include_self=True)
            .only("pk")
        )
        return queryset.filter(pk__in=descendants)
