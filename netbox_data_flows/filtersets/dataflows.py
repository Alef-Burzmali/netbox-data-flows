from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from dcim.models import Device
from ipam.models import Prefix, IPRange, IPAddress
from virtualization.models import VirtualMachine

from netbox_data_flows import models, choices

from .addins import ApplicationFilterSetAddin, InheritedStatusFilterSetAddin
from .filters import (
    ChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
    MultiValueNumberFilter,
    MultiValueNumericArrayFilter,
)

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

    source_is_null = ChoiceFilter(
        choices=choices.TargetIsEmptyChoice,
        method="filter_target_is_null",
    )
    source_aliases = ModelMultipleChoiceFilter(
        queryset=models.ObjectAlias.objects.all(),
        label="Source Object Aliases (ID)",
        method="filter_sources",
    )
    source_prefixes = ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Source Prefix (ID)",
        method="filter_sources",
    )
    source_ipranges = ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        label="Source IP Ranges (ID)",
        method="filter_sources",
    )
    source_ipaddresses = ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="Source IP Addresses (ID)",
        method="filter_sources",
    )
    source_devices = ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Source Devices (any IP address) (ID)",
        method="filter_sources",
    )
    source_virtual_machines = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label="Source Virtual Machine (any IP address) (ID)",
        method="filter_sources",
    )

    destination_is_null = ChoiceFilter(
        choices=choices.TargetIsEmptyChoice,
        method="filter_target_is_null",
    )
    destination_aliases = ModelMultipleChoiceFilter(
        queryset=models.ObjectAlias.objects.all(),
        label="Destination Object Aliases (ID)",
        method="filter_destinations",
    )
    destination_prefixes = ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Destination Prefix (ID)",
        method="filter_destinations",
    )
    destination_ipranges = ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        label="Destination IP Ranges (ID)",
        method="filter_destinations",
    )
    destination_ipaddresses = ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="Destination IP Addresses (ID)",
        method="filter_destinations",
    )
    destination_devices = ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Destination Devices (any IP address) (ID)",
        method="filter_destinations",
    )
    destination_virtual_machines = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label="Destination Virtual Machine (any IP address) (ID)",
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

    # OR all the targets
    def filter_target_is_null(self, queryset, field_name, value):
        if field_name.startswith("source_"):
            setattr(
                self,
                "_sources_is_null",
                value == choices.TargetIsEmptyChoice.STATUS_NULL,
            )
        if field_name.startswith("destination_"):
            setattr(
                self,
                "_destinations_is_null",
                value == choices.TargetIsEmptyChoice.STATUS_NULL,
            )

        return queryset

    def filter_sources(self, queryset, field_name, value):
        self._filter_targets("_sources", field_name, value)
        return queryset

    def filter_destinations(self, queryset, field_name, value):
        self._filter_targets("_destinations", field_name, value)
        return queryset

    def _filter_targets(self, set_name, field_name, value):
        if not value:
            return

        # need to treat that one specially as we
        # cannot OR'ed two querysets
        if field_name.endswith("_aliases"):
            set_name += "_pk"

        if not hasattr(self, set_name):
            setattr(self, set_name, [])
        getattr(self, set_name).extend(value)

    @property
    def qs(self):
        # OR(sources) AND OR(destinations)
        qs = super().qs

        sources = Q()
        if hasattr(self, "_sources_is_null"):
            if self._sources_is_null:
                sources |= Q(sources__exact=None)
            else:
                sources |= ~Q(sources__exact=None)
        if hasattr(self, "_sources_pk"):
            sources |= Q(sources__in=self._sources_pk)
        if hasattr(self, "_sources"):
            sources |= Q(
                sources__in=models.ObjectAlias.objects.contains(*self._sources)
            )

        destinations = Q()
        if hasattr(self, "_destinations_is_null"):
            if self._destinations_is_null:
                destinations |= Q(destinations__exact=None)
            else:
                destinations |= ~Q(destinations__exact=None)
        if hasattr(self, "_destinations_pk"):
            destinations |= Q(destinations__in=self._destinations_pk)
        if hasattr(self, "_destinations"):
            destinations |= Q(
                destinations__in=models.ObjectAlias.objects.contains(
                    *self._destinations
                )
            )

        return qs.filter(sources).filter(destinations).distinct()
