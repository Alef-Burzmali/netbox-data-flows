from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine

from netbox_data_flows import models
from netbox_data_flows.utils.helpers import get_device_ipaddresses

from .filters import ModelMultipleChoiceFilter


__all__ = ("ObjectAliasFilterSet",)


class ObjectAliasFilterSet(NetBoxModelFilterSet):
    prefixes = ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Prefix (ID)",
    )
    ip_ranges = ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        label="IP Range (ID)",
    )
    ip_addresses = ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="IP Address (ID)",
    )
    devices = ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Aliased Devices (any IP address) (ID)",
        method="filter_devices",
    )
    virtual_machines = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label="Aliased Virtual Machine (any IP address) (ID)",
        method="filter_devices",
    )

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

    def filter_devices(self, queryset, name, value):
        if not value:
            return queryset

        ip_addresses = get_device_ipaddresses(*value)
        if not ip_addresses.exists():
            return queryset.none()

        return queryset.filter(ip_addresses__in=ip_addresses)
