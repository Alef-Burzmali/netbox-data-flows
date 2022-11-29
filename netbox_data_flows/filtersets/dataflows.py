from django.db.models import Q
from django_filters import FilterSet

from netbox.filtersets import NetBoxModelFilterSet

from dcim.models import Device
from ipam.models import Prefix, IPAddress
from virtualization.models import VirtualMachine

from netbox_data_flows.models import (
    Application,
    ApplicationRole,
    DataFlow,
)
from netbox_data_flows.choices import (
    DataFlowProtocolChoices,
    DataFlowStatusChoices,
)


from .addins import *
from .filters import *

__all__ = ("DataFlowFilterSet",)


class DataFlowFilterSet(
    ApplicationFilterSetAddin,
    InheritedStatusFilterSetAddin,
    FilterSet,
):

    protocol = MultipleChoiceFilter(
        choices=DataFlowProtocolChoices,
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
        abstract = True

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


class DataFlowFilterSet(NetBoxModelFilterSet, DataFlowFilterSetBase):
    parent_id = TreeNodeMultipleChoiceFilter(
        queryset=DataFlow.objects.all(),
        lookup_expr="in",
        label="Parent (ID)",
    )
    parent = TreeNodeMultipleChoiceFilter(
        queryset=DataFlow.objects.all(),
        lookup_expr="in",
        to_field_name="name",
        label="Parent (name)",
    )

    class Meta:
        model = DataFlow
        fields = (
            "id",
            "name",
            "status",
        )


