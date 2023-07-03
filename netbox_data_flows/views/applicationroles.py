from django.db.models import Count

from netbox.views import generic
from utilities.views import register_model_view

from netbox_data_flows import filtersets, forms, models, tables


__all__ = (
    "ApplicationRoleView",
    "ApplicationRoleListView",
    "ApplicationRoleEditView",
    "ApplicationRoleDeleteView",
    "ApplicationRoleBulkImportView",
    "ApplicationRoleBulkEditView",
    "ApplicationRoleBulkDeleteView",
)


class ApplicationRoleListView(generic.ObjectListView):
    queryset = models.ApplicationRole.objects.annotate(
        application_count=Count("applications", distinct=True),
    )
    table = tables.ApplicationRoleTable
    filterset = filtersets.ApplicationRoleFilterSet


@register_model_view(models.ApplicationRole)
class ApplicationRoleView(generic.ObjectView):
    queryset = models.ApplicationRole.objects.all()

    def get_extra_context(self, request, instance):
        applications_table = tables.ApplicationTable(
            instance.applications.prefetch_related("role").annotate(
                dataflow_count=Count("dataflows", distinct=True),
            )
        )
        applications_table.configure(request)

        return {
            "applications_table": applications_table,
        }


@register_model_view(models.ApplicationRole, "edit")
class ApplicationRoleEditView(generic.ObjectEditView):
    queryset = models.ApplicationRole.objects.all()
    form = forms.ApplicationRoleForm


@register_model_view(models.ApplicationRole, "delete")
class ApplicationRoleDeleteView(generic.ObjectDeleteView):
    queryset = models.ApplicationRole.objects.all()


class ApplicationRoleBulkImportView(generic.BulkImportView):
    queryset = models.ApplicationRole.objects.all()
    model_form = forms.ApplicationRoleImportForm
    table = tables.ApplicationRoleTable


class ApplicationRoleBulkEditView(generic.BulkEditView):
    queryset = models.ApplicationRole.objects.annotate(
        application_count=Count("applications", distinct=True),
    )
    filterset = filtersets.ApplicationRoleFilterSet
    table = tables.ApplicationRoleTable
    form = forms.ApplicationRoleBulkEditForm


class ApplicationRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ApplicationRole.objects.annotate(
        application_count=Count("applications", distinct=True),
    )
    filterset = filtersets.ApplicationRoleFilterSet
    table = tables.ApplicationRoleTable
