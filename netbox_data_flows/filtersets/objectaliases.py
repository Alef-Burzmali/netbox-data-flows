from django.db.models import Q

from extras.models import Tag
from netbox.filtersets import PrimaryModelFilterSet
from utilities.filtersets import register_filterset

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine

from netbox_data_flows import choices, models

from .filters import ModelMultipleChoiceFilter, MultipleChoiceFilter

__all__ = ("ObjectAliasFilterSet",)


@register_filterset
class ObjectAliasFilterSet(PrimaryModelFilterSet):
    matching_type = MultipleChoiceFilter(
        choices=choices.ObjectAliasMatchingChoices,
        method="filter_matching_type",
        label="Target matching type",
    )

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
        method="filter_targets",
    )
    virtual_machines = ModelMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(),
        label="Virtual Machine (any IP address) (ID)",
        method="filter_targets",
    )

    device_tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        label="Device tag (ID)",
    )
    virtual_machine_tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        label="Virtual Machine tag (ID)",
    )

    tag_matching_rule = MultipleChoiceFilter(
        choices=choices.TagMatchingRuleChoices,
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

    def filter_matching_type(self, queryset, name, value):
        if not value:
            return queryset

        self._matching_type = value
        return queryset

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

        matching = dict()
        if hasattr(self, "_matching_type"):
            authorized_matching = set(c[0] for c in choices.ObjectAliasMatchingChoices)
            for value in self._matching_type:
                if value in authorized_matching:
                    matching[value] = True

        if hasattr(self, "_targets"):
            qs = qs.contains(*self._targets, **matching)

        return qs
