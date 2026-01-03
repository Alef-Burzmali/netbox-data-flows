from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from extras.models import Tag
from netbox.models import PrimaryModel
from utilities.data import array_to_string
from utilities.querysets import RestrictedQuerySet

from netbox_data_flows import choices
from netbox_data_flows.constants import DATAFLOW_PORT_MAX, DATAFLOW_PORT_MIN

from .groups import DataFlowGroup
from .objectaliases import ObjectAlias


__all__ = ("DataFlow",)


class DataFlowQuerySet(RestrictedQuerySet):
    def only_disabled(self):
        disabled_groups = DataFlowGroup.objects.only_disabled().only("pk")
        return self.filter(
            models.Q(status=choices.DataFlowStatusChoices.STATUS_DISABLED) | models.Q(group_id__in=disabled_groups)
        )

    def only_enabled(self):
        disabled_groups = DataFlowGroup.objects.only_disabled().only("pk")
        return self.filter(status=choices.DataFlowStatusChoices.STATUS_ENABLED).exclude(group_id__in=disabled_groups)

    def part_of_group_recursive(self, *dataflowgroups, include_direct_children=True):
        group_ids = [getattr(dfg, "pk", dfg) for dfg in dataflowgroups]
        subgroups = (
            DataFlowGroup.objects.filter(pk__in=group_ids)
            .get_descendants(include_self=include_direct_children)
            .only("pk")
        )
        return self.filter(group_id__in=subgroups)

    def sources_or_destinations(self, *objects):
        return self.filter(
            models.Q(sources__in=ObjectAlias.objects.contains(*objects))
            | models.Q(destinations__in=ObjectAlias.objects.contains(*objects))
        ).distinct()

    def sources(self, *objects):
        return self.filter(models.Q(sources__in=ObjectAlias.objects.contains(*objects))).distinct()

    def destinations(self, *objects):
        return self.filter(models.Q(destinations__in=ObjectAlias.objects.contains(*objects))).distinct()


class DataFlow(PrimaryModel):
    """Representation of a data flow for an application."""

    # Inherited fields:
    # description - overwritten
    # comments
    # owner

    name = models.CharField(max_length=200)
    description = models.CharField(
        max_length=500,  # increased from default 200 to 500
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
    tenant = models.ForeignKey(
        to="tenancy.Tenant", on_delete=models.PROTECT, related_name="dataflows", blank=True, null=True
    )

    #
    # Status and inherited status
    #

    status = models.CharField(
        max_length=10,
        choices=choices.DataFlowStatusChoices,
        default=choices.DataFlowStatusChoices.STATUS_ENABLED,
    )

    @cached_property
    def inherited_status(self):
        if self.status == choices.DataFlowStatusChoices.STATUS_DISABLED:
            return self.status
        elif self.group and self.group.inherited_status != choices.DataFlowInheritedStatusChoices.STATUS_ENABLED:
            return choices.DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED
        else:
            return self.status

    @property
    def inherited_status_display(self):
        if self.inherited_status == choices.DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED:
            return choices.DataFlowInheritedStatusChoices.CHOICES[2][1]

        return self.get_status_display()

    def get_status_color(self):
        return choices.DataFlowInheritedStatusChoices.colors.get(self.inherited_status)

    @property
    def inherited_tags(self):
        if not self.pk:
            return []

        if not self.group:
            return self.tags.all()

        return Tag.objects.filter(
            models.Q(dataflow=self.pk) | models.Q(dataflowgroup__in=self.group.get_ancestors(include_self=True))
        ).distinct()

    #
    # Specification
    #

    protocol = models.CharField(
        max_length=10,
        choices=choices.DataFlowProtocolChoices,
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
                MinValueValidator(DATAFLOW_PORT_MIN),
                MaxValueValidator(DATAFLOW_PORT_MAX),
            ]
        ),
        blank=True,
        null=True,
    )
    destination_ports = ArrayField(
        base_field=models.PositiveIntegerField(
            validators=[
                MinValueValidator(DATAFLOW_PORT_MIN),
                MaxValueValidator(DATAFLOW_PORT_MAX),
            ]
        ),
        blank=True,
        null=True,
    )

    @property
    def is_icmp(self):
        return self.protocol in (
            choices.DataFlowProtocolChoices.PROTOCOL_ICMPv4,
            choices.DataFlowProtocolChoices.PROTOCOL_ICMPv6,
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

        if self.is_icmp:
            return self.icmp_type_list

        return array_to_string(self.destination_ports)

    @property
    def icmp_type_list(self):
        if not self.destination_ports:
            return "Any"

        if self.protocol == choices.DataFlowProtocolChoices.PROTOCOL_ICMPv4:
            verbose_names = dict(choices.ICMPv4TypeChoices.CHOICES)
        else:
            verbose_names = dict(choices.ICMPv6TypeChoices.CHOICES)

        ret = []
        for icmp_type in self.destination_ports:
            try:
                ret += [verbose_names[icmp_type]]
            except KeyError:
                ret += f"Type {icmp_type}"

        return ", ".join(ret)

    class Meta:
        ordering = (
            "application",
            "group",
            "name",
        )

    objects = DataFlowQuerySet.as_manager()

    clone_fields = (
        "application",
        "description",
        "destination_ports",
        "destinations",
        "group",
        "owner",
        "protocol",
        "source_ports",
        "sources",
        "status",
        "tenant",
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:dataflow", args=[self.pk])

    def clean(self, *args, **kwargs):
        if self.protocol in (
            choices.DataFlowProtocolChoices.PROTOCOL_ICMPv4,
            choices.DataFlowProtocolChoices.PROTOCOL_ICMPv6,
        ):
            self.source_ports = []

        return super().clean(*args, **kwargs)
