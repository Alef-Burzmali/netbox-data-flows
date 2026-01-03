from django.db import models
from django.urls import reverse

from netbox.models import PrimaryModel
from utilities.querysets import RestrictedQuerySet

from netbox_data_flows.utils.helpers import get_device_ipaddresses


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

        if other := [o for o in objects if o._meta.model_name not in ("prefix", "iprange", "ipaddress")]:
            dev_addresses = []
            for obj in other:
                try:
                    dev_addresses += get_device_ipaddresses(obj)
                except Exception as e:
                    raise TypeError(f"Cannot test if {self.__class__} contains {obj}") from e

            filtering |= models.Q(ip_addresses__in=dev_addresses)

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

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Object Aliases"

    objects = ObjectAliasQuerySet.as_manager()

    clone_fields = (
        "ip_addresses",
        "ip_ranges",
        "owner",
        "prefixes",
    )

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:objectalias", args=[self.pk])

    def __str__(self):
        return self.name
