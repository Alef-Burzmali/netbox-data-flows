import itertools

from django.db import models
from django.urls import reverse

from extras.models import Tag
from netbox.models import PrimaryModel
from utilities.querysets import RestrictedQuerySet

from dcim.models import Device
from ipam.models import IPAddress
from virtualization.models import VirtualMachine

from netbox_data_flows import choices
from netbox_data_flows.utils.helpers import get_device_ipaddresses, get_ipaddress_host

__all__ = ("ObjectAlias",)


class ObjectAliasQuerySet(RestrictedQuerySet):
    def contains(self, *objects, direct=None, indirect=None, tagged=None):
        """Return ObjectAlias containing any one of the objects in parameter.

        If direct is True, an object is contained if it is a direct member of prefixes, ip_ranges or ip_addresses,
        or is a device or virtual machine with an IP in ip_addresses.

        If indirect is True, an object is contained if it is a subset of a prefix or range directly contained.

        If tagged is True, the device_tags and virtual_machine_tags are used. An IP is contained if its parent
        object has the corresponding tag and the following tag_matching_rule is respected:
        - primary: the IP is the primary IPv4 or IPv6 of the object
        - oob: the IP is the OOB IP of the object (only device)
        - all: the IP is assigned to one of the interfaces of the object.

        If all selectors are None, all the selection types are used.
        """
        if direct is None and indirect is None and tagged is None:
            direct, indirect, tagged = True, True, True

        # Split the requested objects in four lists based on their types
        prefixes, ip_ranges, ip_addresses, devices = [], [], [], []
        for obj in objects:
            if obj._meta.model_name == "prefix":
                prefixes.append(obj)
            elif obj._meta.model_name == "iprange":
                ip_ranges.append(obj)
            elif obj._meta.model_name == "ipaddress":
                ip_addresses.append(obj)
            else:
                # devices or virtual machines only, other types will raise TypeError
                try:
                    dev_addresses = get_device_ipaddresses(obj)
                except AttributeError as e:
                    raise TypeError(f"Cannot test if {self.__class__} contains {obj}") from e

                devices.append((obj, dev_addresses))

        filtering = models.Q()
        if direct:
            filtering |= self._contains_direct(prefixes, ip_ranges, ip_addresses, devices)
        if indirect:
            filtering |= self._contains_indirect(prefixes, ip_ranges, ip_addresses, devices)
        if tagged:
            filtering |= self._contains_tagged(ip_addresses, devices)

        # make sure the default filter returns an empty list
        if filtering == models.Q():
            return self.none()

        return self.filter(filtering).distinct()

    def _contains_direct(self, prefixes, ip_ranges, ip_addresses, devices):
        """Return ObjectAlias containing any one of the objects in parameter based on the direct rule."""
        filtering = models.Q()

        if prefixes:
            filtering |= models.Q(prefixes__in=prefixes)
        if ip_ranges:
            filtering |= models.Q(ip_ranges__in=ip_ranges)
        if ip_addresses:
            filtering |= models.Q(ip_addresses__in=ip_addresses)
        if devices:
            dev_addresses = IPAddress.objects.none()
            for dev, ips in devices:
                dev_addresses |= ips
            filtering |= models.Q(ip_addresses__in=dev_addresses)

        return filtering

    def _contains_indirect(self, prefixes, ip_ranges, ip_addresses, devices):
        """Return ObjectAlias containing any one of the objects in parameter based on the indirect rule."""
        filtering = models.Q()

        for prefix in prefixes:
            # aliases with prefixes that are parents of our prefix
            filtering |= models.Q(prefixes__in=prefix.get_parents())

            # aliases with ranges that fully contain our prefix
            # compare host to avoid comparing prefix lengths
            filtering |= models.Q(
                ip_ranges__vrf=prefix.vrf,
                ip_ranges__start_address__host__inet__lte=prefix.prefix.ip,
                ip_ranges__end_address__host__inet__gte=prefix.prefix.broadcast,
            )

        for ip_range in ip_ranges:
            # NetBox IP ranges cannot overlap
            # aliases with prefixes that fully contain our range
            filtering |= models.Q(
                prefixes__vrf=ip_range.vrf,
                prefixes__prefix__net_contains_or_equals=ip_range.start_address,
            ) & models.Q(
                prefixes__vrf=ip_range.vrf,
                prefixes__prefix__net_contains_or_equals=ip_range.end_address,
            )

        for ip_address in ip_addresses:
            # prefixes where passed IP is within prefix
            filtering |= models.Q(prefixes__vrf=ip_address.vrf, prefixes__prefix__net_contains=ip_address.address)
            # ranges where passed IP is within range
            filtering |= models.Q(
                ip_ranges__vrf=ip_address.vrf,
                ip_ranges__start_address__lte=ip_address.address,
                ip_ranges__end_address__gte=ip_address.address,
            )

        for dev_address in itertools.chain.from_iterable(ips for (dev, ips) in devices):
            # prefixes where passed IP is within prefix
            filtering |= models.Q(prefixes__vrf=dev_address.vrf, prefixes__prefix__net_contains=dev_address.address)
            # ranges where passed IP is within range
            filtering |= models.Q(
                ip_ranges__vrf=dev_address.vrf,
                ip_ranges__start_address__lte=dev_address.address,
                ip_ranges__end_address__gte=dev_address.address,
            )

        return filtering

    def _contains_tagged(self, ip_addresses, devices):
        """Return ObjectAliases matching any one of the objects in parameters based on their tags."""
        # Six possible combination based on type (Device/VM) and matching rule (All, Primary, OOB)
        # But VM do not have oob ips
        device_tag_all_ips = []
        vm_tag_all_ips = []
        device_tag_primary_ips = []
        vm_tag_primary_ips = []
        device_tag_oob_ips = []

        for ip_address in ip_addresses:
            host = get_ipaddress_host(ip_address)
            if isinstance(host, Device):
                device_tag_all_ips.extend(host.tags.all())
                if ip_address == host.primary_ip4 or ip_address == host.primary_ip6:
                    device_tag_primary_ips.extend(host.tags.all())
                if ip_address == host.oob_ip:
                    device_tag_oob_ips.extend(host.tags.all())

            elif isinstance(host, VirtualMachine):
                vm_tag_all_ips.extend(host.tags.all())
                if ip_address == host.primary_ip4 or ip_address == host.primary_ip6:
                    vm_tag_primary_ips.extend(host.tags.all())

        for obj, dev_addresses in devices:
            # Ensure that the device has at least one address
            if not dev_addresses.exists():
                continue

            if obj._meta.model_name == "device":
                tags = list(obj.tags.all())
                device_tag_all_ips.extend(tags)
                if obj.primary_ip4 or obj.primary_ip6:
                    device_tag_primary_ips.extend(tags)
                if obj.oob_ip:
                    device_tag_oob_ips.extend(tags)

            elif obj._meta.model_name == "virtualmachine":
                tags = list(obj.tags.all())
                vm_tag_all_ips.extend(tags)
                if obj.primary_ip4 or obj.primary_ip6:
                    vm_tag_primary_ips.extend(tags)

        filtering = models.Q()

        if device_tag_all_ips:
            filtering |= models.Q(
                device_tags__in=device_tag_all_ips,
                tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_ALL,
            )
        if vm_tag_all_ips:
            filtering |= models.Q(
                virtual_machine_tags__in=vm_tag_all_ips,
                tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_ALL,
            )
        if device_tag_primary_ips:
            filtering |= models.Q(
                device_tags__in=device_tag_primary_ips,
                tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_PRIMARY,
            )
        if vm_tag_primary_ips:
            filtering |= models.Q(
                virtual_machine_tags__in=vm_tag_primary_ips,
                tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_PRIMARY,
            )
        if device_tag_oob_ips:
            filtering |= models.Q(
                device_tags__in=device_tag_oob_ips,
                tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_OOB,
            )

        return filtering


class ObjectAlias(PrimaryModel):
    """
    Source or Destination of a Data Flow.

    Can contain any number of:
    * IPAddress
    * Prefix
    * IPRange
    in direct assignments

    IPAddresses can also be matched via device_tags and
    virtual_machine_tags.
    """

    # Inherited fields:
    # description
    # comments
    # owner

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The name of the ObjectAlias",
    )

    # Our targets
    prefixes = models.ManyToManyField(
        "ipam.Prefix",
        related_name="data_flow_object_aliases",
    )
    ip_ranges = models.ManyToManyField(
        "ipam.IPRange",
        related_name="data_flow_object_aliases",
    )
    ip_addresses = models.ManyToManyField(
        "ipam.IPAddress",
        related_name="data_flow_object_aliases",
    )
    device_tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="data_flow_device_object_aliases",
    )
    virtual_machine_tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="data_flow_virtual_machine_object_aliases",
    )
    tag_matching_rule = models.CharField(
        max_length=10,
        choices=choices.TagMatchingRuleChoices,
        default=choices.TagMatchingRuleChoices.MATCHING_PRIMARY,
    )

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Object Aliases"
        indexes = [
            models.Index(fields=["tag_matching_rule"]),
        ]

    objects = ObjectAliasQuerySet.as_manager()

    clone_fields = (
        "device_tags",
        "ip_addresses",
        "ip_ranges",
        "owner",
        "prefixes",
        "virtual_machine_tags",
        "tag_matching_rule",
    )

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:objectalias", args=[self.pk])

    def __str__(self):
        return self.name

    def get_tag_matching_rule_color(self):
        return choices.TagMatchingRuleChoices.colors.get(self.tag_matching_rule)

    def get_resolved_ip_addresses(self, *, include_direct_assignments=True):
        device_tag_qs = self.device_tags.all()
        virtual_machine_tag_qs = self.virtual_machine_tags.all()

        matching_rule = {"primary": False, "oob": False}
        if self.tag_matching_rule == "primary":
            matching_rule["primary"] = True
        elif self.tag_matching_rule == "oob":
            matching_rule["oob"] = True

        results = IPAddress.objects.none()

        if include_direct_assignments:
            results |= self.ip_addresses.all()

        if device_tag_qs.exists():
            devices = Device.objects.filter(tags__in=device_tag_qs).distinct()
            results |= get_device_ipaddresses(*devices, **matching_rule)

        if virtual_machine_tag_qs.exists():
            virtual_machines = VirtualMachine.objects.filter(tags__in=virtual_machine_tag_qs).distinct()
            results |= get_device_ipaddresses(*virtual_machines, **matching_rule)

        return results.distinct()
