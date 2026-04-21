from django.db import models
from django.urls import reverse

from extras.models import Tag
from netbox.models import PrimaryModel
from utilities.querysets import RestrictedQuerySet

from dcim.models import Device
from ipam.models import IPAddress
from virtualization.models import VirtualMachine

from netbox_data_flows.utils.helpers import get_device_ipaddresses, get_ipaddress_host

__all__ = ("ObjectAlias",)


class ObjectAliasQuerySet(RestrictedQuerySet):
    def contains(self, *objects):
        """Return ObjectAlias containing any one of the objects in parameter."""
        filtering = models.Q()
        if prefixes := [o for o in objects if o._meta.model_name == "prefix"]:
            filtering |= models.Q(prefixes__in=prefixes)
        if ip_ranges := [o for o in objects if o._meta.model_name == "iprange"]:
            filtering |= models.Q(ip_ranges__in=ip_ranges)
        if ip_addresses := [o for o in objects if o._meta.model_name == "ipaddress"]:
            filtering |= models.Q(ip_addresses__in=ip_addresses)

            host_device_tags = []
            host_virtual_machine_tags = []
            for ip_address in ip_addresses:
                host = get_ipaddress_host(ip_address)
                if isinstance(host, Device):
                    host_device_tags.extend(host.tags.all())
                elif isinstance(host, VirtualMachine):
                    host_virtual_machine_tags.extend(host.tags.all())

            if host_device_tags:
                filtering |= models.Q(device_tags__in=host_device_tags)
            if host_virtual_machine_tags:
                filtering |= models.Q(virtual_machine_tags__in=host_virtual_machine_tags)

        if other := [o for o in objects if o._meta.model_name not in ("prefix", "iprange", "ipaddress")]:
            dev_addresses = []
            device_tags = []
            virtual_machine_tags = []
            for obj in other:
                try:
                    addresses = get_device_ipaddresses(obj)
                except Exception as e:
                    raise TypeError(f"Cannot test if {self.__class__} contains {obj}") from e

                if addresses.exists():
                    dev_addresses += addresses
                    if obj._meta.model_name == "device":
                        device_tags.extend(obj.tags.all())
                    elif obj._meta.model_name == "virtualmachine":
                        virtual_machine_tags.extend(obj.tags.all())

            if dev_addresses:
                filtering |= models.Q(ip_addresses__in=dev_addresses)
            if device_tags:
                filtering |= models.Q(device_tags__in=device_tags)
            if virtual_machine_tags:
                filtering |= models.Q(virtual_machine_tags__in=virtual_machine_tags)

        return self.filter(filtering).distinct()


class ObjectAlias(PrimaryModel):
    """
    Source or Destination of a Data Flow.

    Can contain any number of:
    * IPAddress
    * Prefix
    * IPRange
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

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Object Aliases"

    objects = ObjectAliasQuerySet.as_manager()

    clone_fields = (
        "device_tags",
        "ip_addresses",
        "ip_ranges",
        "owner",
        "prefixes",
        "virtual_machine_tags",
    )

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:objectalias", args=[self.pk])

    def __str__(self):
        return self.name

    def get_resolved_ip_addresses(self):
        device_tag_qs = self.device_tags.all()
        virtual_machine_tag_qs = self.virtual_machine_tags.all()

        query = models.Q(pk__in=self.ip_addresses.values("pk"))

        if device_tag_qs.exists():
            devices = Device.objects.filter(tags__in=device_tag_qs).distinct()
            query |= models.Q(pk__in=get_device_ipaddresses(*devices).values("pk"))

        if virtual_machine_tag_qs.exists():
            virtual_machines = VirtualMachine.objects.filter(tags__in=virtual_machine_tag_qs).distinct()
            query |= models.Q(pk__in=get_device_ipaddresses(*virtual_machines).values("pk"))

        return IPAddress.objects.filter(query).distinct()
