from django.db.models import Q

from netbox.filtersets import NetBoxModelFilterSet, BaseFilterSet

from dcim.models import Device
from ipam.models import Prefix, IPRange, IPAddress
from virtualization.models import VirtualMachine

from netbox_data_flows import models
from netbox_data_flows.utils.helpers import get_device_ipaddresses

from .filters import ModelMultipleChoiceFilter


__all__ = (
    "ObjectAliasTargetFilterSet",
    "ObjectAliasFilterSet",
)


class ObjectAliasTargetFilterSet(BaseFilterSet):
    prefixes = ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Aliased Prefix (ID)",
        method="filter_targets",
    )
    ipranges = ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        label="Aliased IP Ranges (ID)",
        method="filter_targets",
    )
    ipaddresses = ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="Aliased IP Addresses (ID)",
        method="filter_targets",
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
        model = models.ObjectAliasTarget
        fields = ("id",)

    def search(self, queryset, name, value):
        return queryset

    def filter_devices(self, queryset, name, value):
        if not value:
            return queryset

        ip_addresses = get_device_ipaddresses(*value)
        if not ip_addresses.exists():
            return queryset.none()

        return self.filter_targets(queryset, name, ip_addresses)

    # OR all the targets
    # First, build a list
    def filter_targets(self, queryset, name, value):
        if not value:
            return queryset

        if not hasattr(self, "_targets"):
            setattr(self, "_targets", [])

        self._targets += list(value)

        return queryset

    # Second, match against that list
    @property
    def qs(self):
        # OR(targets)
        qs = super().qs

        if hasattr(self, "_targets"):
            qs = qs.contains(*self._targets)

        return qs


class ObjectAliasFilterSet(NetBoxModelFilterSet, ObjectAliasTargetFilterSet):
    targets = ModelMultipleChoiceFilter(
        queryset=models.ObjectAliasTarget.objects.all(),
        label="Target object (ID)",
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
