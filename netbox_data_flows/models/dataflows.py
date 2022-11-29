from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from mptt.models import MPTTModel, TreeForeignKey

from netbox.models import NetBoxModel
from utilities.mptt import TreeManager
from utilities.utils import array_to_string

from ipam.constants import SERVICE_PORT_MIN, SERVICE_PORT_MAX

from netbox_data_flows.choices import (
    DataFlowProtocolChoices,
    DataFlowStatusChoices,
    DataFlowInheritedStatusChoices,
)

from .applications import Application
from .objectaliases import ObjectAlias


__all__ = ("DataFlow",)


class DataFlowBase(MPTTModel):
    """Base implementation of a data flow between a source and a destination"""

    parent = TreeForeignKey(
        to="self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
        db_index=True,
    )
    name = models.CharField(max_length=100, db_column="description")
    comments = models.TextField(blank=True)

    # status and inherited status
    status = models.CharField(
        max_length=10,
        choices=DataFlowStatusChoices,
        default=DataFlowStatusChoices.STATUS_ENABLED,
    )

    @cached_property
    def inherited_status(self):
        if self.status == DataFlowStatusChoices.STATUS_DISABLED:
            return self.status
        elif (
            self.get_ancestors(include_self=False)
            .filter(status=DataFlowStatusChoices.STATUS_DISABLED)
            .exists()
        ):
            return DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED
        else:
            return self.status

    @property
    def inherited_status_display(self):
        if (
            self.inherited_status
            == DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED
        ):
            return DataFlowInheritedStatusChoices.CHOICES[2][1]

        return self.get_status_display()

    def get_status_color(self):
        if (
            self.inherited_status
            == DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED
        ):
            return DataFlowInheritedStatusChoices.CHOICES[2][2]
        else:
            return DataFlowStatusChoices.colors.get(self.status)

    protocol = models.CharField(
        max_length=10,
        choices=DataFlowProtocolChoices,
        blank=True,
    )
    sources = models.ManyToManyField(
        ObjectAlias,
        related_name="dataflow_sources",
    )
    destinations = models.ManyToManyField(
        ObjectAlias,
        related_name="dataflow_destinations",
    )

    # ports
    source_ports = ArrayField(
        base_field=models.PositiveIntegerField(
            validators=[
                MinValueValidator(SERVICE_PORT_MIN),
                MaxValueValidator(SERVICE_PORT_MAX),
            ]
        ),
        blank=True,
        null=True,
    )
    destination_ports = ArrayField(
        base_field=models.PositiveIntegerField(
            validators=[
                MinValueValidator(SERVICE_PORT_MIN),
                MaxValueValidator(SERVICE_PORT_MAX),
            ]
        ),
        blank=True,
        null=True,
    )

    @property
    def source_port_list(self):
        if not self.source_ports:
            return "Any"

        return array_to_string(self.source_ports)

    @property
    def destination_port_list(self):
        if not self.destination_ports:
            return "Any"

        return array_to_string(self.destination_ports)


    class Meta:
        abstract = True

    class MPTTMeta:
        order_insertion_by = ("name",)

    objects = TreeManager()

    @classmethod
    def get_disabled_queryset(cls):
        return cls.objects.filter(
            status=DataFlowStatusChoices.STATUS_DISABLED
        ).get_descendants(include_self=True)

    def clean(self):
        super().clean()

        # An MPTT model cannot be its own parent
        if (
            self.pk
            and self.parent
            and self.parent in self.get_descendants(include_self=True)
        ):
            raise ValidationError(
                {
                    "parent": f"Cannot assign self or child {self._meta.verbose_name} as parent."
                }
            )



class DataFlow(DataFlowBase, NetBoxModel):
    """Representation of a data flow for an application"""

    application = models.ForeignKey(
        to=Application,
        on_delete=models.CASCADE,
        related_name="dataflows",
    )

    class Meta:
        ordering = (
            "application",
            "name",
        )
        constraints = (
            models.UniqueConstraint(
                fields=("parent", "name"),
                name="netbox_data_flows_dataflow_parent_name",
            ),
            models.UniqueConstraint(
                fields=("application", "name"),
                name="netbox_data_flows_dataflow_application_name",
                condition=models.Q(parent=None),
            ),
        )

    clone_fields = (
        "application",
        "parent",
        "status",
        "name",
        "comments",
        "protocol",
        "source_ports",
        "destination_ports",
        "sources",
        "destinations",
    )

    @property
    def description(self):
        return str(self)

    def __str__(self):
        return f"{self.application}: {self.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:dataflow", args=[self.pk])

    def clean(self):
        super().clean()

        # There must be a source or a destination
        if not self.sources and not self.destinations:
            raise ValidationError(
                "At least a Source or a Destination must be given."
            )

        if self.parent and self.parent.application != self.application:
            raise ValidationError(
                "A child data flow must be applied to the same application as its parent data flow."
            )

        # update all our descendants' application
        if self.pk:
            self.get_descendants().update(application_id=self.application)

    def validate_unique(self, exclude=None):
        if self.parent is None:
            dataflows = DataFlow.objects.exclude(pk=self.pk)
            if dataflows.filter(
                name=self.name,
                application=self.application,
                parent__isnull=True,
            ).exists():
                raise ValidationError(
                    {
                        "name": "A data flow with this name already exists for this application."
                    }
                )

        super().validate_unique(exclude=exclude)
