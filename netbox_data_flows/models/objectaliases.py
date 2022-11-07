import math

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel

from netbox_data_flows.choices import ObjectAliasTypeChoices


__all__ = (
    "ObjectAlias",
    "ObjectAliasTarget",
    "OBJECTALIAS_ASSIGNMENT_MODELS",
)


# Object types allowed in aliases
OBJECTALIAS_ASSIGNMENT_MODELS = models.Q(
    models.Q(app_label="ipam", model="prefix")
    | models.Q(app_label="ipam", model="iprange")
    | models.Q(app_label="ipam", model="ipaddress")
)


class ObjectAliasTarget(models.Model):
    """
    A single prefix, range or IP address to be used in ObjectAlias.

    Provide a common interface for working with different DCIM types and a
    type for Many-to-Many generic relationships with any of these types.
    """

    @classmethod
    def get_target(cls, *targets):
        query = models.Q()
        for t in targets:
            ct = ContentType.objects.get_for_model(t.__class__)
            query |= models.Q(aliased_object_type=ct, aliased_object_id=t.pk)

        return cls.objects.filter(query)

    @classmethod
    def get_or_create(cls, target):
        """Return an existing instance for this target or create one"""
        instance = cls.get_target(target).first()
        if not instance:
            instance = cls(aliased_object=target)

        return instance

    type = models.CharField(
        editable=False,
        max_length=5,
        choices=ObjectAliasTypeChoices,
        default=ObjectAliasTypeChoices.TYPE_NETWORK,
    )
    aliased_object_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=OBJECTALIAS_ASSIGNMENT_MODELS,
        on_delete=models.CASCADE,
        related_name="+",
    )
    aliased_object_id = models.PositiveBigIntegerField()
    aliased_object = GenericForeignKey(
        ct_field="aliased_object_type",
        fk_field="aliased_object_id",
    )

    class Meta:
        ordering = (
            "type",
            "aliased_object_id",
        )
        constraints = (
            models.UniqueConstraint(
                fields=("aliased_object_type", "aliased_object_id"),
                name="netbox_data_flows_objectaliastarget_type_id",
            ),
        )

    def get_absolute_url(self):
        return self.aliased_object.get_absolute_url()

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self._model == "ipaddress":
            address = str(self.aliased_object).split("/")[0]
            if self.parent:
                return f"{self.parent} ({address})"
            else:
                return address
        else:
            return str(self.aliased_object)

    @property
    def parent(self):
        if self._model == "ipaddress":
            try:
                return self.aliased_object.assigned_object.parent_object
            except AttributeError:
                return None
        else:
            return None

    @property
    def size(self):
        if self._model == "ipaddress":
            return 1
        elif self._model == "iprange":
            return self.aliased_object.size
        elif self._model == "prefix":
            return 2**self.aliased_object.mask_length
        else:
            raise RuntimeError(
                f"ObjectAliasTarget has a unsupported model: {self._model}"
            )

    @property
    def family(self):
        return self.aliased_object.family

    @property
    def _model(self):
        return self.aliased_object_type.model

    def __contains__(self, other):
        assert isinstance(
            other, self.__class__
        ), f"{self.__class__} can only be compared to other {self.__class__}"

        own_model = self._model
        own = self.aliased_object
        other_model = other._model
        other = other.aliased_object

        if own_model == "ipaddress":
            return (other_model == "ipaddress") and (
                other.address == own.address
            )

        elif own_model == "iprange":
            if other_model == "ipaddress":
                return other.address in own.range
            elif other_model == "iprange":
                return other.range in own.range
            elif other_model == "prefix":
                return other.prefix in own.range
            else:
                raise RuntimeError(
                    f"ObjectAliasTarget has a unsupported model: {other_model}"
                )

        elif own_model == "prefix":
            if other_model == "ipaddress":
                return other.address in own.prefix
            elif other_model == "iprange":
                return other.range in own.prefix
            elif other_model == "prefix":
                return other.prefix in own.prefix
            else:
                raise RuntimeError(
                    f"ObjectAliasTarget has a unsupported model: {other_model}"
                )

        else:
            raise RuntimeError(
                f"ObjectAliasTarget has a unsupported model: {own_model}"
            )

    def _compute_type(self):
        if self._model == "ipaddress":
            self.type = ObjectAliasTypeChoices.TYPE_HOST
        else:
            self.type = ObjectAliasTypeChoices.TYPE_NETWORK

    def save(self, *args, **kwargs):
        self._compute_type()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        self._compute_type()


class ObjectAlias(NetBoxModel):
    """Source or Destination of a Data Flow"""

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The name of the ObjectAlias",
    )
    description = models.CharField(
        max_length=100,
        blank=True,
    )
    size = models.PositiveSmallIntegerField(
        editable=False,
        default=0,
        help_text="The size of the ObjectAlias's networks or hosts, for sorting",
    )
    type = models.CharField(
        editable=False,
        max_length=5,
        choices=ObjectAliasTypeChoices,
        default=ObjectAliasTypeChoices.TYPE_NETWORK,
        help_text="The type of ObjectAlias's targets",
    )

    targets = models.ManyToManyField(
        ObjectAliasTarget,
        related_name="aliases",
    )

    class Meta:
        ordering = (
            "type",
            "name",
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            # clean() has ensured all children have the same type
            self.type = self.targets[0].type

            size = sum(t.size for t in self.targets)
            self.size = int(math.log2(size))

        super().save(*args, **kwargs)

    def clean(self):
        super().clean()

        if not self.pk:
            return

        if not self.targets:
            raise ValidationError(
                "The ObjectAlias must have a least one target"
            )

        self.type = self.targets[0].type
        if not all(t.type == self.type for t in self.targets):
            raise ValidationError(
                "The ObjectAlias must contain only networks (Prefix or Range) OR hosts (IP Addresses)"
            )
