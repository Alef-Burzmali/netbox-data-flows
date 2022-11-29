from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from netbox.models import NestedGroupModel

from netbox_data_flows.choices import (
    DataFlowStatusChoices,
    DataFlowInheritedStatusChoices,
)

from .applications import Application


__all__ = ("DataFlowGroup",)


class DataFlowGroup(NestedGroupModel):
    """Hierachical group of Data Flows associated to one application"""

    # Inherited fields:
    # parent
    # name
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

    @classmethod
    def get_disabled_queryset(cls):
        return cls.objects.filter(
            status__in=(
                DataFlowInheritedStatusChoices.STATUS_DISABLED,
                DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED,
            )
        )

    def get_absolute_url(self):
        return reverse(
            "plugins:netbox_data_flows:dataflowgroup", args=[self.pk]
        )

    def clean(self):
        super().clean()

        if self.parent and self.parent.application != self.application:
            raise ValidationError(
                "The same application must be applied to both parent and child data flow groups."
            )

        # update all our descendants' application
        if self.pk:
            self.get_descendants().update(application_id=self.application)

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
                        "name": "A data flow with this name already exists for this application."
                    }
                )

        super().validate_unique(exclude=exclude)
