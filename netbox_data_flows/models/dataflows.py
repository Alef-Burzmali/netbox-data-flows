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


__all__ = (
    "DataFlow",
    "DataFlowTemplate",
)


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
            if self.source or self.destination:
                return "Any"

        return array_to_string(self.source_ports)

    @property
    def destination_port_list(self):
        if not self.destination_ports:
            if self.source or self.destination:
                return "Any"

        return array_to_string(self.destination_ports)

    # sources
    source_prefix = models.ForeignKey(
        to="ipam.Prefix",
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    source_device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    source_virtual_machine = models.ForeignKey(
        to="virtualization.VirtualMachine",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    source_ipaddress = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Source IP address",
    )

    @property
    def source(self):
        return (
            self.source_prefix
            or self.source_device
            or self.source_virtual_machine
            or self.source_ipaddress
            or None
        )

    # destination
    destination_prefix = models.ForeignKey(
        to="ipam.Prefix",
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    destination_device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="+",
        blank=True,
        null=True,
    )
    destination_virtual_machine = models.ForeignKey(
        to="virtualization.VirtualMachine",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )
    destination_ipaddress = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
        verbose_name="Destination IP address",
    )

    @property
    def destination(self):
        return (
            self.destination_prefix
            or self.destination_device
            or self.destination_virtual_machine
            or self.destination_ipaddress
            or None
        )

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

        # A Data Flow must have at most 1 type of sources
        sources = 0
        if self.source_prefix:
            sources += 1
        if self.source_device:
            sources += 1
        if self.source_virtual_machine:
            sources += 1
        if self.source_ipaddress:
            sources += 1

        if sources > 1:
            raise ValidationError(
                "A data flow cannot be associated with several types of sources. Use children data flows instead."
            )

        # A Data Flow must have at most 1 type of destinations
        destinations = 0
        if self.destination_prefix:
            destinations += 1
        if self.destination_device:
            destinations += 1
        if self.destination_virtual_machine:
            destinations += 1
        if self.destination_ipaddress:
            destinations += 1

        if destinations > 1:
            raise ValidationError(
                "A data flow cannot be associated with several types of destinations. Use children data flows instead."
            )

        # If we have a start of specification, ensure it is complete
        if (
            self.protocol
            or self.destination_ports
            or self.source_ports
            or self.source
            or self.destination
        ):
            # If there is a specification, there must be a protocol
            if not self.protocol:
                raise ValidationError(
                    {
                        "protocol": "A Protocol is mandatory if a specification is given."
                    }
                )

            # If there is a specification, there must be a source or a destination
            if not self.source and not self.destination:
                raise ValidationError(
                    "At least a Source or a Destination is mandatory if a specification is given."
                )


class DataFlowTemplate(DataFlowBase, NetBoxModel):
    """A template of a data flow between sources and destinations"""

    class Meta:
        ordering = ("name",)
        constraints = (
            models.UniqueConstraint(
                fields=("parent", "name"),
                name="netbox_data_flows_dataflowtemplate_parent_name",
            ),
            models.UniqueConstraint(
                fields=("name",),
                name="netbox_data_flows_dataflowtemplate_name",
                condition=models.Q(parent=None),
            ),
        )

    clone_fields = (
        "parent",
        "name",
        "status",
        "comments",
        "protocol",
        "source_ports",
        "destination_ports",
        "source_device",
        "source_prefix",
        "source_ipaddress",
        "source_virtual_machine",
        "destination_device",
        "destination_ipaddress",
        "destination_prefix",
        "destination_virtual_machine",
    )

    def __str__(self):
        return f"Template: {self.name}"

    def get_absolute_url(self):
        return reverse(
            "plugins:netbox_data_flows:dataflowtemplate", args=[self.pk]
        )

    def clean(self):
        super().clean()

        if self.parent and not isinstance(self.parent, self.__class__):
            raise ValidationError(
                "Only a DataFlowTemplate can be the parent of another DataFlowTemplate (error during clone)"
            )

    def validate_unique(self, exclude=None):
        if self.parent is None:
            dataflows = DataFlowTemplate.objects.exclude(pk=self.pk)
            if dataflows.filter(name=self.name, parent__isnull=True).exists():
                raise ValidationError(
                    {
                        "name": "A data flow template with this name already exists."
                    }
                )

        super().validate_unique(exclude=exclude)


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
        "source_device",
        "source_prefix",
        "source_ipaddress",
        "source_virtual_machine",
        "destination_device",
        "destination_ipaddress",
        "destination_prefix",
        "destination_virtual_machine",
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

        if self.parent and not isinstance(self.parent, self.__class__):
            raise ValidationError(
                "Only a DataFlow can be the parent of another DataFlow (error during clone)"
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
