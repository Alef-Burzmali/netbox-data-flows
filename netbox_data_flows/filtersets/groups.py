from extras.filters import TagFilter, TagIDFilter
from netbox.filtersets import NestedGroupModelFilterSet
from utilities.filtersets import register_filterset

from tenancy.filtersets import TenancyFilterSet

from netbox_data_flows import models

from .addins import ApplicationFilterSetAddin, InheritedStatusFilterSetAddin
from .filters import ModelMultipleChoiceFilter


__all__ = ("DataFlowGroupFilterSet",)


@register_filterset
class DataFlowGroupFilterSet(
    ApplicationFilterSetAddin,
    InheritedStatusFilterSetAddin,
    TenancyFilterSet,
    NestedGroupModelFilterSet,
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

    inherited_tag = TagFilter(method="filter_inherited_tags")
    inherited_tag_id = TagIDFilter(method="filter_inherited_tags")

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "status",
        )

    def filter_ancestors(self, queryset, name, value):
        if not value:
            return queryset

        ancestors = [getattr(dfg, "pk", dfg) for dfg in value]
        descendants = (
            models.DataFlowGroup.objects.filter(pk__in=ancestors).get_descendants(include_self=True).only("pk")
        )
        return queryset.filter(pk__in=descendants)

    def filter_inherited_tags(self, queryset, name, value):
        if not value:
            return queryset

        # Perform a AND search - like regular tags
        # based on conjoined queries
        for tag in value:
            queryset = queryset.filter(tags=tag).get_descendants(include_self=True)

        return queryset
