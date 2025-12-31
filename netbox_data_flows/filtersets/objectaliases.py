from django.db.models import Q

from netbox.filtersets import PrimaryModelFilterSet
from utilities.filtersets import register_filterset

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine

from netbox_data_flows import models
from netbox_data_flows.utils.helpers import get_device_ipaddresses

from .filters import ModelMultipleChoiceFilter


__all__ = ("ObjectAliasFilterSet",)


@register_filterset
class ObjectAliasFilterSet(PrimaryModelFilterSet):
    prefixes = ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(),
        label="Prefix (ID)",
        method="filter_targets",
    )
    ip_ranges = ModelMultipleChoiceFilter(
        queryset=IPRange.objects.all(),
        label="IP Ranges (ID)",
        method="filter_targets",
    )
    ip_addresses = ModelMultipleChoiceFilter(
        queryset=IPAddress.objects.all(),
        label="IP Addresses (ID)",
        method="filter_targets",
    )
    devices = ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label="Devices (any IP address) (ID)",
        method="filter_devices",
    )
    virtual_machines = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label="Virtual Machine (any IP address) (ID)",
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

    def filter_devices(self, queryset, name, value):
        if not value:
            return queryset

        ip_addresses = get_device_ipaddresses(*value)
        if not ip_addresses.exists():
            return queryset.none()

        return self.filter_targets(queryset, name, ip_addresses)
