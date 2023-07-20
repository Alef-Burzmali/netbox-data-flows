from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet
from utilities.utils import array_to_string

from ipam.constants import SERVICE_PORT_MIN, SERVICE_PORT_MAX

from netbox_data_flows.choices import (
    DataFlowProtocolChoices,
    DataFlowStatusChoices,
    DataFlowInheritedStatusChoices,
)
from netbox_data_flows.utils.helpers import object_list_to_string

from .groups import DataFlowGroup
from .objectaliases import ObjectAlias


__all__ = ("DataFlow",)


class DataFlowQuerySet(RestrictedQuerySet):
    def only_disabled(self):
        disabled_groups = DataFlowGroup.objects.only_disabled().only("pk")
        return self.filter(
            models.Q(status=DataFlowStatusChoices.STATUS_DISABLED)
            | models.Q(group_id__in=disabled_groups)
        )

    def only_enabled(self):
        disabled_groups = DataFlowGroup.objects.only_disabled().only("pk")
        return self.filter(
            status=DataFlowStatusChoices.STATUS_ENABLED
        ).exclude(group_id__in=disabled_groups)

    def part_of_group_recursive(
        self, *dataflowgroups, include_direct_children=True
    ):
        group_ids = [getattr(dfg, "pk", dfg) for dfg in dataflowgroups]
        subgroups = (
            DataFlowGroup.objects.filter(pk__in=group_ids)
            .get_descendants(include_self=include_direct_children)
            .only("pk")
        )
        return self.filter(group_id__in=subgroups)

    def sources_or_destinations(self, *targets):
        return self.filter(
            models.Q(sources__in=ObjectAlias.objects.contains(*targets))
            | models.Q(destinations__in=ObjectAlias.objects.contains(*targets))
        ).distinct()

    def sources(self, *targets):
        return self.filter(
            models.Q(sources__in=ObjectAlias.objects.contains(*targets))
        ).distinct()

    def destinations(self, *targets):
        return self.filter(
            models.Q(destinations__in=ObjectAlias.objects.contains(*targets))
        ).distinct()


class DataFlow(NetBoxModel):
    """Representation of a data flow for an application"""

    name = models.CharField(max_length=200)
    description = models.CharField(
        max_length=500,
        blank=True,
    )
    application = models.ForeignKey(
        to="Application",
        on_delete=models.CASCADE,
        related_name="dataflows",
        blank=True,
        null=True,
        db_index=True,
    )
    group = models.ForeignKey(
        to="DataFlowGroup",
        on_delete=models.CASCADE,
        related_name="dataflows",
        blank=True,
        null=True,
    )
    comments = models.TextField(blank=True)

    #
    # Status and inherited status
    #

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
            self.group
            and self.group.inherited_status
            != DataFlowInheritedStatusChoices.STATUS_ENABLED
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
        return DataFlowInheritedStatusChoices.colors.get(self.inherited_status)

    #
    # Specification
    #

    protocol = models.CharField(
        max_length=10,
        choices=DataFlowProtocolChoices,
    )
    sources = models.ManyToManyField(
        to="ObjectAlias",
        related_name="dataflow_sources",
    )
    destinations = models.ManyToManyField(
        to="ObjectAlias",
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

    @property
    def source_list(self):
        sources = self.sources.all()
        return object_list_to_string(sources, linkify=True)

    @property
    def destination_list(self):
        destinations = self.destinations.all()
        return object_list_to_string(destinations, linkify=True)

    class Meta:
        ordering = (
            "application",
            "group",
            "name",
        )

    objects = DataFlowQuerySet.as_manager()

    clone_fields = (
        "application",
        "group",
        "description",
        "status",
        "comments",
        "protocol",
        "source_ports",
        "destination_ports",
        "sources",
        "destinations",
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:dataflow", args=[self.pk])
