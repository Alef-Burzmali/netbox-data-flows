from django.db.models import Q
from django_filters import FilterSet

from netbox.filtersets import NetBoxModelFilterSet

from netbox_data_flows import models, choices

from .addins import *
from .filters import *

__all__ = ("DataFlowFilterSet",)


class DataFlowFilterSet(
    ApplicationFilterSetAddin,
    InheritedStatusFilterSetAddin,
    NetBoxModelFilterSet,
):
    group_id = ModelMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        label="Group, direct membership (ID)",
    )
    group = ModelMultipleChoiceFilter(
        field_name="group__name",
        queryset=models.DataFlowGroup.objects.all(),
        to_field_name="name",
        label="Group, direct membership (name)",
    )
    recursive_group_id = ModelMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        label="Group, recursive membership (ID)",
        method="filter_recursive_groups",
    )
    recursive_group = ModelMultipleChoiceFilter(
        queryset=models.DataFlowGroup.objects.all(),
        to_field_name="name",
        label="Group, recursive membership (name)",
        method="filter_recursive_groups",
    )

    protocol = MultipleChoiceFilter(
        choices=choices.DataFlowProtocolChoices,
    )
    source_ports = MultiValueNumericArrayFilter(
        method="filter_ports",
    )
    destination_ports = MultiValueNumberFilter(
        method="filter_ports",
    )

    sources = ModelMultipleChoiceFilter(
        queryset=models.ObjectAlias.objects.all(),
        label="Sources (ID)",
    )
    destinations = ModelMultipleChoiceFilter(
        queryset=models.ObjectAlias.objects.all(),
        label="Destinations (ID)",
    )

    class Meta:
        model = models.DataFlow
        fields = (
            "id",
            "name",
            "status",
        )

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset

        return queryset.filter(name__icontains=value)

    def filter_recursive_groups(self, queryset, field_name, value):
        if not value:
            return queryset

        return queryset.part_of_group_recursive(*value)

    # OR(source_ports) AND OR(destination_ports)
    def filter_ports(self, queryset, field_name, value):
        if not value:
            return queryset

        if field_name == "source_ports":
            field_db = "source_ports__contains"
        else:
            field_db = "destination_ports__contains"

        query = Q()
        for port in value:
            query |= Q(**{field_db: [port]})

        return queryset.filter(query)

    def filter_sources(self, queryset, field_name, value):
        # TODO
        return queryset

    def filter_destinations(self, queryset, field_name, value):
        # TODO
        return queryset
