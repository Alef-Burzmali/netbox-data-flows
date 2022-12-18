from django.db.models import Q
from django_filters import FilterSet

from netbox_data_flows import models, choices

from .filters import ModelMultipleChoiceFilter, ChoiceFilter


__all__ = (
    "ApplicationFilterSetAddin",
    "InheritedStatusFilterSetAddin",
)


class ApplicationFilterSetAddin(FilterSet):
    class Meta:
        abstract = True

    application_id = ModelMultipleChoiceFilter(
        queryset=models.Application.objects.all(),
        label="Application (ID)",
    )
    application = ModelMultipleChoiceFilter(
        queryset=models.Application.objects.all(),
        label="Application (Name)",
    )

    application_role = ModelMultipleChoiceFilter(
        queryset=models.ApplicationRole.objects.all(),
        label="Application Roles",
        method="filter_application_role",
    )

    def filter_application_role(self, queryset, field_name, value):
        if not value:
            return queryset

        return queryset.filter(application__role__in=[v.pk for v in value])


class InheritedStatusFilterSetAddin(FilterSet):
    class Meta:
        abstract = True

    status = ChoiceFilter(
        choices=choices.DataFlowStatusChoices,
    )

    inherited_status = ChoiceFilter(
        choices=choices.DataFlowStatusChoices,
        method="filter_inherited_status",
    )

    def filter_inherited_status(self, queryset, field_name, value):
        if not value:
            return queryset

        if value == choices.DataFlowStatusChoices.STATUS_DISABLED:
            queryset = queryset.only_disabled()
        else:
            queryset = queryset.only_enabled()

        return queryset
