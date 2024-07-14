from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from netbox_data_flows import models

from .addins import ApplicationFilterSetAddin, InheritedStatusFilterSetAddin
from .filters import ModelMultipleChoiceFilter

__all__ = ("DataFlowGroupFilterSet",)


class DataFlowGroupFilterSet(
    ApplicationFilterSetAddin,
    InheritedStatusFilterSetAddin,
    NetBoxModelFilterSet,
):
    parent_id = ModelMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        label="Parent (ID)",
    )
    parent = ModelMultipleChoiceFilter(
        field_name="parent__slug",
        queryset=models.DataFlowGroup.objects.all(),
        to_field_name="slug",
        label="Parent (slug)",
    )
    ancestor_id = ModelMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        label="Ancestor (ID)",
        method="filter_ancestors",
    )
    ancestor = ModelMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        to_field_name="slug",
        label="Ancestor (slug)",
        method="filter_ancestors",
    )

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "status",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset

        qs_filter = Q(name__icontains=value) | Q(description__icontains=value) | Q(slug__icontains=value)
        return queryset.filter(qs_filter)

    def filter_ancestors(self, queryset, name, value):
        if not value:
            return queryset

        ancestors = [getattr(dfg, "pk", dfg) for dfg in value]
        descendants = (
            models.DataFlowGroup.objects.filter(pk__in=ancestors).get_descendants(include_self=True).only("pk")
        )
        return queryset.filter(pk__in=descendants)
