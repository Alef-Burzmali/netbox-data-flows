from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from netbox.models import NestedGroupModel
from utilities.mptt import TreeManager, TreeQuerySet

from netbox_data_flows.choices import (
    DataFlowStatusChoices,
    DataFlowInheritedStatusChoices,
)

from .applications import Application


__all__ = ("DataFlowGroup",)


class DataFlowGroupQuerySet(TreeQuerySet):
    def only_disabled(self):
        return self.filter(
            status=DataFlowStatusChoices.STATUS_DISABLED
        ).get_descendants(include_self=True)

    def only_enabled(self):
        return self.exclude(pk__in=self.only_disabled().only("pk"))


class DataFlowGroupManager(
    models.Manager.from_queryset(DataFlowGroupQuerySet), TreeManager
):
    pass


class DataFlowGroup(NestedGroupModel):
    """Hierachical group of Data Flows associated to one application"""

    # Inherited fields:
    # parent
    # name
    # slug
    # description

    application = models.ForeignKey(
        to=Application,
        on_delete=models.CASCADE,
        related_name="dataflow_groups",
        blank=True,
        null=True,
        db_index=True,
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
        return DataFlowInheritedStatusChoices.colors.get(self.inherited_status)

    class Meta:
        ordering = (
            "application",
            "name",
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
        "parent",
        "description",
        "status",
        "comments",
    )

    def get_absolute_url(self):
        return reverse(
            "plugins:netbox_data_flows:dataflowgroup", args=[self.pk]
        )

    def validate_unique(self, exclude=None):
        if self.parent is None:
            groups = self.__class__.objects.exclude(pk=self.pk)
            if groups.filter(
                name=self.name,
                application=self.application,
                parent__isnull=True,
            ).exists():
                raise ValidationError(
                    {
                        "name": (
                            "A data flow with this name already exists for "
                            "this application."
                        )
                    }
                )

        super().validate_unique(exclude=exclude)
