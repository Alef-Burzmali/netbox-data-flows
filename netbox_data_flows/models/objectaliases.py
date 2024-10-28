from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from core.models import ObjectType
from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet

from ipam.models import IPAddress, IPRange, Prefix

from netbox_data_flows.utils.helpers import get_assignment_querystring, get_device_ipaddresses


__all__ = (
    "ObjectAlias",
    "ObjectAliasTarget",
)


# Object types allowed in aliases
OBJECTALIAS_ASSIGNMENT_OBJECTS = (
    Prefix,
    IPRange,
    IPAddress,
)
OBJECTALIAS_ASSIGNMENT_MODELS = (
    ("ipam", "prefix"),
    ("ipam", "iprange"),
    ("ipam", "ipaddress"),
)
OBJECTALIAS_ASSIGNMENT_QS = get_assignment_querystring(OBJECTALIAS_ASSIGNMENT_MODELS)


class ObjectAliasTargetQuerySet(RestrictedQuerySet):
    def contains(self, *objects):
        """Return ObjectAliasTarget containing any one of the objects in parameter."""
        # FIXME: Lazy load
        ip_ct = ObjectType.objects.get_for_model(IPAddress)

        if not objects:
            return self.none()

        query = models.Q()
        for t in objects:
            ct = ObjectType.objects.get_for_model(t.__class__)

            if (ct.app_label, ct.model) in OBJECTALIAS_ASSIGNMENT_MODELS:
                query |= models.Q(target_type=ct, target_id=t.pk)
            else:
                try:
                    ip_addresses = get_device_ipaddresses(t)
                except Exception as e:
                    raise Exception(f"Cannot test if {self.__class__} contains {t}") from e

                query |= models.Q(target_type=ip_ct, target_id__in=ip_addresses)

        return self.filter(query)


class ObjectAliasTarget(models.Model):
    """
    A single prefix, range or IP address to be used in ObjectAlias.

    Provide a common interface for working with different DCIM types and a
    type for Many-to-Many generic relationships with any of these types.

    This object is intended to be transparent to the user.
    """

    _netbox_private = True

    @classmethod
    def get_or_create(cls, target):
        """Return an existing instance for this target or create one."""
        instance = cls.objects.contains(target).first()
        if not instance:
            # FIXME: target._meta
            ct = ObjectType.objects.get_for_model(target.__class__)
            type = (ct.app_label, ct.model)

            if type not in OBJECTALIAS_ASSIGNMENT_MODELS:
                raise TypeError(f"Unsupported type {':'.join(type)} for ObjectAliasTarget")

            instance = cls(target=target)

        return instance

    target_type = models.ForeignKey(
        to="contenttypes.ContentType",
        limit_choices_to=OBJECTALIAS_ASSIGNMENT_QS,
        on_delete=models.PROTECT,
        related_name="+",
    )
    target_id = models.PositiveBigIntegerField()
    target = GenericForeignKey(
        ct_field="target_type",
        fk_field="target_id",
    )

    class Meta:
        ordering = (
            "target_type",
            "target_id",
        )
        constraints = (
            models.UniqueConstraint(
                fields=("target_type", "target_id"),
                name="netbox_data_flows_objectaliastarget_type_id",
            ),
        )

    objects = ObjectAliasTargetQuerySet.as_manager()

    def get_absolute_url(self):
        return self.target.get_absolute_url()

    def __str__(self):
        return self.name

    @property
    def type_verbose_name(self):
        return self.target._meta.verbose_name

    @property
    def name(self):
        if self._model == "ipaddress":
            if self.parent:
                return f"{self.target} ({self.parent})"
            else:
                return str(self.target)
        else:
            return str(self.target)

    @property
    def parent(self):
        if self._model == "ipaddress":
            try:
                return self.target.assigned_object.parent_object
            except AttributeError:
                return None
        elif self._model == "prefix":
            try:
                return self.target.vlan
            except AttributeError:
                return None
        else:
            return None

    @property
    def family(self):
        try:
            return self.target.family
        except AttributeError:
            return None

    @property
    def _model(self):
        return self.target_type.model

    def save(self, *args, **kwargs):
        if self.target_type:
            type = (self.target_type.app_label, self.target_type.model)
            if type not in OBJECTALIAS_ASSIGNMENT_MODELS:
                raise ValidationError(f"Unsupported type {':'.join(type)} for ObjectAliasTarget")

        super().save(*args, **kwargs)


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


class ObjectAlias(NetBoxModel):
    """
    Source or Destination of a Data Flow.

    Can contain any number of:
    * IPAddress
    * Prefix
    * IPRange
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The name of the ObjectAlias",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )
    comments = models.TextField(blank=True)

    # We cannot have ManyToMany relations to GenericForeignKeys, hence the
    # intermediary Target type
    targets = models.ManyToManyField(
        ObjectAliasTarget,
        related_name="aliases",
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

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:objectalias", args=[self.pk])

    def __str__(self):
        return self.name
