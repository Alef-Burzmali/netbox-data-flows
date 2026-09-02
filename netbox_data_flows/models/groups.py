from django.contrib.postgres.indexes import GistIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from extras.models import Tag
from netbox.models import NestedLtreeGroupModel
from netbox.models.ltree import LtreeManager, LtreeQuerySet

from netbox_data_flows.choices import DataFlowInheritedStatusChoices, DataFlowStatusChoices
from netbox_data_flows.utils.tags import AccessibleTagsMixin

from .applications import Application

__all__ = ("DataFlowGroup",)


class DataFlowGroupQuerySet(LtreeQuerySet):
    def only_disabled(self):
        return self.filter(status=DataFlowStatusChoices.STATUS_DISABLED).get_descendants(include_self=True)

    def only_enabled(self):
        return self.exclude(pk__in=self.only_disabled().only("pk"))

    def get_descendants(self, include_self=False):
        lookup = "descendant_or_equal" if include_self else "descendant"

        path_filter = models.Q()
        for path in self.only("path").values_list("path", flat=True):
            path_filter |= models.Q(**{f"path__{lookup}": path})

        if not path_filter:
            return self.none()

        return self.model.objects.filter(path_filter).distinct()


class DataFlowGroupManager(models.Manager.from_queryset(DataFlowGroupQuerySet), LtreeManager):
    pass


class DataFlowGroup(AccessibleTagsMixin, NestedLtreeGroupModel):
    """Hierachical group of Data Flows."""

    # Inherited fields:
    # name
    # slug
    # parent
    # owner
    # description
    # comments

    application = models.ForeignKey(
        to=Application,
        on_delete=models.CASCADE,
        related_name="dataflow_groups",
        blank=True,
        null=True,
        db_index=True,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant", on_delete=models.PROTECT, related_name="dataflowgroups", blank=True, null=True
    )

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
        elif self.get_ancestors(include_self=False).filter(status=DataFlowStatusChoices.STATUS_DISABLED).exists():
            return DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED
        else:
            return self.status

    @property
    def inherited_status_display(self):
        if self.inherited_status == DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED:
            return DataFlowInheritedStatusChoices.CHOICES[2][1]

        return self.get_status_display()

    def get_status_color(self):
        return DataFlowInheritedStatusChoices.colors.get(self.inherited_status)

    @property
    def inherited_tags(self):
        if not self.pk:
            return []

        return Tag.objects.filter(
            netbox_data_flows_dataflowgroup_tagged__in=self.get_ancestors(include_self=True)
        ).distinct()

    class Meta:
        ordering = ("sort_path",)
        indexes = (
            GistIndex(fields=["path"], name="netbox_data_flows_dfg_path_gist"),
            models.Index(fields=["sort_path"], name="netbox_data_flows_dfg_spath_ix"),
        )
        constraints = (
            models.UniqueConstraint(
                fields=("parent", "name"),
                name="netbox_data_flows_dataflowgroup_parent_name",
            ),
            models.UniqueConstraint(
                fields=("application", "name"),
                name="netbox_data_flows_dataflowgroup_application_name",
                condition=models.Q(parent=None),
            ),
        )

    objects = DataFlowGroupManager()

    clone_fields = (
        "application",
        "owner",
        "parent",
        "status",
        "tenant",
    )

    def get_absolute_url(self):
        return reverse("plugins:netbox_data_flows:dataflowgroup", args=[self.pk])

    def validate_unique(self, exclude=None):
        if self.parent is None:
            groups = self.__class__.objects.exclude(pk=self.pk)
            if groups.filter(
                name=self.name,
                application=self.application,
                parent__isnull=True,
            ).exists():
                raise ValidationError({"name": "A data flow group with this name already exists for this application."})

        super().validate_unique(exclude=exclude)
