from django.db.models import Count

from netbox.views import generic

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


class ApplicationView(generic.ObjectView):
    queryset = models.Application.objects.prefetch_related(
        "role", "dataflows", "dataflow_groups"
    )

    def get_extra_context(self, request, instance):
        dataflowgroups_table = tables.DataFlowGroupTable(
            instance.dataflow_groups.all().annotate(
                dataflow_count=Count("dataflows", distinct=True),
            )
        )
        dataflowgroups_table.configure(request)

        dataflows_table = tables.DataFlowTable(instance.dataflows.all())
        dataflows_table.configure(request)

        return {
            "dataflowgroups_table": dataflowgroups_table,
            "dataflows_table": dataflows_table,
        }


class ApplicationListView(generic.ObjectListView):
    queryset = models.Application.objects.prefetch_related("role").annotate(
        dataflow_count=Count("dataflows"),
    )
    table = tables.ApplicationTable
    filterset = filtersets.ApplicationFilterSet
    filterset_form = forms.ApplicationFilterForm


class ApplicationEditView(generic.ObjectEditView):
    queryset = models.Application.objects.prefetch_related("role")
    form = forms.ApplicationForm


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
    queryset = models.Application.objects.annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable
