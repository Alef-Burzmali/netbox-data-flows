from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet

from ipam.models import Prefix, IPRange, IPAddress

from netbox_data_flows.utils.helpers import get_assignment_querystring
from netbox_data_flows.utils.helpers import get_device_ipaddresses


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
OBJECTALIAS_ASSIGNMENT_QS = get_assignment_querystring(
    OBJECTALIAS_ASSIGNMENT_MODELS
)


class ObjectAliasTargetQuerySet(RestrictedQuerySet):
    def contains(self, *objects):
        """
        Return ObjectAliasTarget containing any one of the objects in parameter
        """
        ip_ct = ContentType.objects.get_for_model(IPAddress)

        if not objects:
            return self.none()

        query = models.Q()
        for t in objects:
            ct = ContentType.objects.get_for_model(t.__class__)

            if (ct.app_label, ct.model) in OBJECTALIAS_ASSIGNMENT_MODELS:
                query |= models.Q(target_type=ct, target_id=t.pk)
            else:
                try:
                    ip_addresses = get_device_ipaddresses(t)
                except Exception as e:
                    raise Exception(
                        f"Cannot test if {self.__class__} contains {t}"
                    ) from e

                query |= models.Q(
                    target_type=ip_ct, target_id__in=ip_addresses
                )

        return self.filter(query)


class ObjectAliasTarget(models.Model):
    """
    A single prefix, range or IP address to be used in ObjectAlias.

    Provide a common interface for working with different DCIM types and a
    type for Many-to-Many generic relationships with any of these types.

    This object is intended to be transparent to the user.
    """

    @classmethod
    def get_or_create(cls, target):
        """Return an existing instance for this target or create one"""
        instance = cls.objects.contains(target).first()
        if not instance:
            ct = ContentType.objects.get_for_model(target.__class__)
            type = (ct.app_label, ct.model)

            if type not in OBJECTALIAS_ASSIGNMENT_MODELS:
                raise TypeError(
                    f"Unsupported type {':'.join(type)} for ObjectAliasTarget"
                )

            instance = cls(target=target)

        return instance

    target_type = models.ForeignKey(
        to=ContentType,
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
        ordering = ("target_id",)
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

    def __contains__(self, other: "ObjectAliasTarget"):
        """Return True if other is fully contained in this ObjectAliasTarget"""

        if not isinstance(other, self.__class__):
            raise TypeError(
                f"{self.__class__} can only be compared to other "
                f"{self.__class__}, not {type(other)}"
            )

        attr_mapping = {
            "ipaddress": "address",
            "iprange": "range",
            "prefix": "prefix",
        }

        if self._model == "ipaddress":
            return (other._model == "ipaddress") and (
                other.target.address == self.target.address
            )

        try:
            own_value = getattr(self.target, attr_mapping[self._model])
        except KeyError:
            raise RuntimeError(
                f"ObjectAliasTarget has a unsupported model: {self._model}"
            )

        try:
            other_value = getattr(other.target, attr_mapping[other._model])
        except KeyError:
            raise RuntimeError(
                f"ObjectAliasTarget has a unsupported model: {other._model}"
            )

        return other_value in own_value

    def save(self, *args, **kwargs):
        if self.target_type:
            type = (self.target_type.app_label, self.target_type.model)
            if type not in OBJECTALIAS_ASSIGNMENT_MODELS:
                raise ValidationError(
                    f"Unsupported type {':'.join(type)} for ObjectAliasTarget"
                )

        super().save(*args, **kwargs)


class ObjectAliasQuerySet(RestrictedQuerySet):
    def contains(self, *objects):
        """
        Return ObjectAlias containing any one of the objects in parameter
        """
        targets = ObjectAliasTarget.objects.contains(*objects)
        return self.filter(targets__in=targets).distinct()


class ObjectAlias(NetBoxModel):
    """Source or Destination of a Data Flow"""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The name of the ObjectAlias",
    )
    description = models.CharField(
        max_length=200,
        blank=True,
    )

    # We cannot have ManyToMany relations to GenericForeignKeys, hence the
    # intermediary Target type
    targets = models.ManyToManyField(
        ObjectAliasTarget,
        related_name="aliases",
    )

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Object Aliases"

    objects = ObjectAliasQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:objectalias", args=[self.pk])

    def __str__(self):
        return self.name

    def __contains__(self, other: "ObjectAlias"):
        """Return True if other is fully contained in this ObjectAlias"""

        if isinstance(other, self.__class__):
            return all(t in self for t in other.targets.all())

        try:
            return any(other in t for t in self.targets.all())
        except TypeError as e:
            raise TypeError(
                f"{self.__class__} cannot be compared with {type(other)}"
            ) from e
