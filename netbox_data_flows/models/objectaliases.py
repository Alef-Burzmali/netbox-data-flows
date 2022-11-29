import math

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet


__all__ = (
    "ObjectAlias",
    "ObjectAliasTarget",
)


# Object types allowed in aliases
# TODO: Add connector to ObjectAlias
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

    This object is intended to be transparent to the user.
    """

    @classmethod
    def get_target(cls, *targets):
        query = models.Q()
        for t in targets:
            ct = ContentType.objects.get_for_model(t.__class__)
            query |= models.Q(target_type=ct, target_id=t.pk)

        return cls.objects.filter(query)

    @classmethod
    def get_or_create(cls, target):
        """Return an existing instance for this target or create one"""
        instance = cls.get_target(target).first()
        if not instance:
            instance = cls(target=target)

        return instance

    target_type = models.ForeignKey(
        to=ContentType,
        limit_choices_to=OBJECTALIAS_ASSIGNMENT_MODELS,
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

    objects = RestrictedQuerySet.as_manager()

    def get_absolute_url(self):
        return self.target.get_absolute_url()

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self._model == "ipaddress":
            address = str(self.target).split("/")[0]
            if self.parent:
                return f"{self.parent} ({address})"
            else:
                return address
        else:
            return str(self.target)

    @property
    def parent(self):
        if self._model == "ipaddress":
            try:
                return self.target.assigned_object.parent_object
            except AttributeError:
                return None
        else:
            return None

    @property
    def size(self):
        if self._model == "ipaddress":
            return 1
        elif self._model == "iprange":
            return self.target.size
        elif self._model == "prefix":
            return 2**self.target.mask_length
        else:
            raise RuntimeError(
                f"ObjectAliasTarget has a unsupported model: {self._model}"
            )

    @property
    def family(self):
        return self.target.family

    @property
    def _model(self):
        return self.target_type.model

    def __contains__(self, other):
        assert isinstance(
            other, self.__class__
        ), f"{self.__class__} can only be compared to other {self.__class__}"

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
    size = models.PositiveSmallIntegerField(
        editable=False,
        default=0,
        help_text="The size of the ObjectAlias's networks or hosts, for sorting",
    )

    # We cannot have ManyToMany relations to GenericForeignKeys, hence the
    # intermediary Target type
    targets = models.ManyToManyField(
        ObjectAliasTarget,
        related_name="aliases",
    )

    class Meta:
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:objectalias", args=[self.pk])

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            # Compute our logarithmic size
            if self.targets:
                size = sum(t.size for t in self.targets)
                self.size = int(math.log2(size))
            else:
                self.size = 0

        super().save(*args, **kwargs)
