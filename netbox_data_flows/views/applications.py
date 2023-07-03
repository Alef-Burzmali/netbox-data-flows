from django.db.models import Count

from netbox.views import generic
from utilities.views import register_model_view

from tenancy.views import ObjectContactsView

from netbox_data_flows import filtersets, forms, models, tables


__all__ = (
    "ApplicationView",
    "ApplicationListView",
    "ApplicationEditView",
    "ApplicationDeleteView",
    "ApplicationBulkImportView",
    "ApplicationBulkEditView",
    "ApplicationBulkDeleteView",
)


class ApplicationListView(generic.ObjectListView):
    queryset = models.Application.objects.prefetch_related("role").annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    table = tables.ApplicationTable
    filterset = filtersets.ApplicationFilterSet
    filterset_form = forms.ApplicationFilterForm


@register_model_view(models.Application)
class ApplicationView(generic.ObjectView):
    queryset = models.Application.objects.prefetch_related(
        "role", "contacts", "dataflows", "dataflow_groups"
    )

    def get_extra_context(self, request, instance):
        dataflowgroups_table = tables.DataFlowGroupTable(
            instance.dataflow_groups.prefetch_related(
                "application",
                "application__role",
                "parent",
            ).annotate(
                dataflow_count=Count("dataflows", distinct=True),
            )
        )
        dataflowgroups_table.configure(request)

        dataflows_table = tables.DataFlowTable(
            instance.dataflows.prefetch_related(
                "application",
                "application__role",
                "group",
                "sources",
                "destinations",
            )
        )
        dataflows_table.configure(request)

        return {
            "dataflowgroups_table": dataflowgroups_table,
            "dataflows_table": dataflows_table,
        }


@register_model_view(models.Application, "edit")
class ApplicationEditView(generic.ObjectEditView):
    queryset = models.Application.objects.prefetch_related("role")
    form = forms.ApplicationForm


@register_model_view(models.Application, "delete")
class ApplicationDeleteView(generic.ObjectDeleteView):
    queryset = models.Application.objects.all()


class ApplicationBulkImportView(generic.BulkImportView):
    queryset = models.Application.objects.all()
    model_form = forms.ApplicationImportForm
    table = tables.ApplicationTable


class ApplicationBulkEditView(generic.BulkEditView):
    queryset = models.Application.objects.prefetch_related("role").annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable
    form = forms.ApplicationBulkEditForm


class ApplicationBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Application.objects.prefetch_related("role").annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable


@register_model_view(models.Application, "contacts")
class ApplicationContactsView(ObjectContactsView):
    queryset = models.Application.objects.all()
