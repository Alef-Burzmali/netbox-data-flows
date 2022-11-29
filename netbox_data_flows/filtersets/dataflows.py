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

from .filters import (
    ChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
    MultiValueNumberFilter,
    MultiValueNumericArrayFilter,
    TreeNodeMultipleChoiceFilter,
)


__all__ = ("DataFlowFilterSet",)



class DataFlowFilterSetBase(FilterSet):
    inherited_status = ChoiceFilter(
        choices=DataFlowStatusChoices,
        method="filter_inherited_status",
    )

    protocol = MultipleChoiceFilter(
        choices=DataFlowProtocolChoices,
    )
    source_ports = MultiValueNumericArrayFilter(
        method="filter_ports",
    )
    destination_ports = MultiValueNumberFilter(
        method="filter_ports",
    )

    source_device_id = ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Device (ID)",
        method="filter_sources",
    )
    source_device = ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Device (Name)",
        method="filter_sources",
    )
    source_virtual_machine_id = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label="VirtualMachine (ID)",
        method="filter_sources",
    )
    source_virtual_machine = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label="VirtualMachine (Name)",
        method="filter_sources",
    )
    source_prefix_id = ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Prefix (ID)",
        method="filter_sources",
    )
    source_prefix = ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Prefix (Name)",
        method="filter_sources",
    )
    source_ipaddress_id = ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="IPAddress (ID)",
        method="filter_sources",
    )
    source_ipaddress = ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="IPAddress (Name)",
        method="filter_sources",
    )

    destination_device_id = ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Device (ID)",
        method="filter_destinations",
    )
    destination_device = ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Device (Name)",
        method="filter_destinations",
    )
    destination_virtual_machine_id = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label="VirtualMachine (ID)",
        method="filter_destinations",
    )
    destination_virtual_machine = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label="VirtualMachine (Name)",
        method="filter_destinations",
    )
    destination_prefix_id = ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Prefix (ID)",
        method="filter_destinations",
    )
    destination_prefix = ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Prefix (Name)",
        method="filter_destinations",
    )
    destination_ipaddress_id = ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="IPAddress (ID)",
        method="filter_destinations",
    )
    destination_ipaddress = ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="IPAddress (Name)",
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

    # OR all the sources
    def filter_sources(self, queryset, field_name, value):
        if not hasattr(self, "_sources"):
            setattr(self, "_sources", {})

        self._sources[field_name] = value
        return queryset

    # OR all the destinations
    def filter_destinations(self, queryset, field_name, value):
        if not hasattr(self, "_destinations"):
            setattr(self, "_destinations", {})

        self._destinations[field_name] = value
        return queryset

    def filter_inherited_status(self, queryset, field_name, value):
        if not value:
            return queryset

        disabled = self.Meta.model.get_disabled_queryset().only("pk")

        if value == DataFlowStatusChoices.STATUS_DISABLED:
            queryset = queryset.filter(pk__in=disabled)
        else:
            queryset = queryset.exclude(pk__in=disabled)

        return queryset

    @property
    def qs(self):
        # OR(sources) AND OR(destinations)
        qs = super().qs

        if hasattr(self, "_sources"):
            query = Q()
            for key, values in self._sources.items():
                for v in values:
                    query |= Q(**{key: v})

            qs = qs.filter(query)

        if hasattr(self, "_destinations"):
            query = Q()
            for key, values in self._destinations.items():
                for v in values:
                    query |= Q(**{key: v})

            qs = qs.filter(query)

        return qs


class DataFlowFilterSet(NetBoxModelFilterSet, DataFlowFilterSetBase):
    application_id = ModelMultipleChoiceFilter(
        queryset=Application.objects.all(),
        label="Application (ID)",
    )
    application = ModelMultipleChoiceFilter(
        queryset=Application.objects.all(),
        label="Application (Name)",
    )

    application_role = ModelMultipleChoiceFilter(
        queryset=ApplicationRole.objects.all(),
        label="Application Roles",
        method="filter_application_role",
    )

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

    def filter_application_role(self, queryset, field_name, value):
        if not value:
            return queryset

        return queryset.filter(application__role__in=[v.pk for v in value])

