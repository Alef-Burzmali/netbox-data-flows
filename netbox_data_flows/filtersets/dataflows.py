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

    protocol = MultipleChoiceFilter(
        choices=choices.DataFlowProtocolChoices,
    )
    source_ports = MultiValueNumericArrayFilter(
        method="filter_ports",
    )
    destination_ports = MultiValueNumberFilter(
        method="filter_ports",
    )

    sources_id = ModelMultipleChoiceFilter(
        queryset=models.ObjectAlias.objects.all(),
        label="Sources (ID)",
        method="filter_sources",
    )
    sources = ModelMultipleChoiceFilter(
        queryset=models.ObjectAlias.objects.all(),
        label="Sources (Name)",
        method="filter_sources",
    )

    destinations_id = ModelMultipleChoiceFilter(
        queryset=models.ObjectAlias.objects.all(),
        label="Destinations (ID)",
        method="filter_destinations",
    )
    destinations = ModelMultipleChoiceFilter(
        queryset=models.ObjectAlias.objects.all(),
        label="Destinations (Name)",
        method="filter_destinations",
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
