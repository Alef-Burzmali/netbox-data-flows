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
        field_name="application__name",
        queryset=models.Application.objects.all(),
        label="Application (Name)",
        to_field_name="name",
    )

    application_role_id = ModelMultipleChoiceFilter(
        field_name="application__role",
        queryset=models.ApplicationRole.objects.all(),
        label="Application Roles (ID)",
    )
    application_role = ModelMultipleChoiceFilter(
        field_name="application__role__slug",
        queryset=models.ApplicationRole.objects.all(),
        label="Application Roles (slug)",
        to_field_name="slug",
    )


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
