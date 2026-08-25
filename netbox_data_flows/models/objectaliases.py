from django.db import models
from django.urls import reverse
from netaddr.ip import IPNetwork

from extras.models import Tag
from netbox.models import PrimaryModel
from utilities.querysets import RestrictedQuerySet

from dcim.models import Device
from ipam.models import IPAddress
from virtualization.models import VirtualMachine

from netbox_data_flows import choices
from netbox_data_flows.utils.helpers import get_device_ipaddresses, get_ipaddress_host

__all__ = ("ObjectAlias",)


# TODO: REFACTOR


class ObjectAliasQuerySet(RestrictedQuerySet):
    def contains(self, *objects):
        """Return ObjectAlias containing any one of the objects in parameter."""
        # make sure the default filter returns an empty list
        filtering = models.Q(name=None)

        if prefixes := [o for o in objects if o._meta.model_name == "prefix"]:
            filtering |= models.Q(prefixes__in=prefixes)
        if ip_ranges := [o for o in objects if o._meta.model_name == "iprange"]:
            filtering |= models.Q(ip_ranges__in=ip_ranges)
        if ip_addresses := [o for o in objects if o._meta.model_name == "ipaddress"]:
            filtering |= models.Q(ip_addresses__in=ip_addresses)
        if other := [o for o in objects if o._meta.model_name not in ("prefix", "iprange", "ipaddress")]:
            dev_addresses = []
            for obj in other:
                try:
                    addresses = get_device_ipaddresses(obj)
                except Exception as e:
                    raise TypeError(f"Cannot test if {self.__class__} contains {obj}") from e

                if addresses.exists():
                    dev_addresses += addresses

            if dev_addresses:
                filtering |= models.Q(ip_addresses__in=dev_addresses)

        return self.filter(filtering).distinct()

    def contains_tagged(self, *objects):
        """Return ObjectAliases matching any one of the objects in parameters based on their tags."""
        # make sure the default filter returns an empty list
        filtering = models.Q(name=None)

        device_tag_all_ips = []
        vm_tag_all_ips = []
        device_tag_primary_ips = []
        vm_tag_primary_ips = []
        device_tag_oob_ips = []
        # vm do not have oob ips

        for obj in objects:
            if obj._meta.model_name == "ipaddress":
                ip_address = obj

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

            elif obj._meta.model_name not in ("prefix", "iprange", "ipaddress"):
                try:
                    addresses = get_device_ipaddresses(obj)
                except Exception as e:
                    raise TypeError(f"Cannot test if {self.__class__} contains {obj}") from e

                # Ensure that the device has at least one address
                if not addresses.exists():
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

        if device_tag_all_ips:
            filtering |= models.Q(
                device_tags__in=device_tag_all_ips, tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_ALL
            )
        if vm_tag_all_ips:
            filtering |= models.Q(
                vm_tags__in=vm_tag_all_ips, tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_ALL
            )
        if device_tag_primary_ips:
            filtering |= models.Q(
                device_tags__in=device_tag_primary_ips,
                tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_PRIMARY,
            )
        if vm_tag_primary_ips:
            filtering |= models.Q(
                vm_tags__in=vm_tag_primary_ips, tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_PRIMARY
            )
        if device_tag_oob_ips:
            filtering |= models.Q(
                device_tags__in=device_tag_oob_ips, tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_OOB
            )

        return self.filter(filtering).distinct()

    def related_to(self, *objects):
        """Return ObjectAlias related to any one of the objects in parameter.

        A object is related if it is within a prefix or range of the ObjectAlias.
        """
        # make sure the default filter returns an empty list
        filtering = models.Q(name=None)

        if prefixes := [o for o in objects if o._meta.model_name == "prefix"]:
            for prefix in prefixes:
                network_address = IPNetwork(f"{prefix.prefix.network}/{prefix.prefix.prefixlen}")
                broadcast_address = IPNetwork(f"{prefix.prefix.broadcast}/{prefix.prefix.prefixlen}")

                # prefixes where passed prefix is within prefix
                filtering |= models.Q(prefixes__vrf=prefix.vrf, prefixes__prefix__net_contains=prefix.prefix)
                # ranges where passed prefix is within or equals range
                filtering |= models.Q(
                    ip_ranges__vrf=prefix.vrf,
                    ip_ranges__start_address__lte=network_address,
                    ip_ranges__end_address__gte=broadcast_address,
                )
        if ip_ranges := [o for o in objects if o._meta.model_name == "iprange"]:
            for ip_range in ip_ranges:
                # prefixes where passed range is within or equals prefix
                filtering |= models.Q(
                    prefixes__vrf=ip_range.vrf, prefixes__prefix__net_contains_or_equals=ip_range.start_address
                ) & models.Q(prefixes__vrf=ip_range.vrf, prefixes__prefix__net_contains_or_equals=ip_range.end_address)
        if ip_addresses := [o for o in objects if o._meta.model_name == "ipaddress"]:
            for ip_address in ip_addresses:
                # prefixes where passed IP is within prefix
                filtering |= models.Q(prefixes__vrf=ip_address.vrf, prefixes__prefix__net_contains=ip_address.address)
                # ranges where passed IP is within range
                filtering |= models.Q(
                    ip_ranges__vrf=ip_address.vrf,
                    ip_ranges__start_address__lte=ip_address.address,
                    ip_ranges__end_address__gte=ip_address.address,
                )

        if other := [o for o in objects if o._meta.model_name not in ("prefix", "iprange", "ipaddress")]:
            dev_addresses = []
            for obj in other:
                try:
                    dev_addresses += get_device_ipaddresses(obj)
                except Exception as e:
                    raise TypeError(f"Cannot test if {self.__class__} is related to {obj}") from e

            for dev_address in dev_addresses:
                # prefixes where passed IP is within prefix
                filtering |= models.Q(prefixes__vrf=dev_address.vrf, prefixes__prefix__net_contains=dev_address.address)
                # ranges where passed IP is within range
                filtering |= models.Q(
                    ip_ranges__vrf=dev_address.vrf,
                    ip_ranges__start_address__lte=dev_address.address,
                    ip_ranges__end_address__gte=dev_address.address,
                )

        return self.filter(filtering).distinct()


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
