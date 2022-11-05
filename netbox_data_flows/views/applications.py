from django.db.models import Count

from netbox.views import generic

from ipam.tables import ServiceTable

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
    queryset = models.Application.objects.prefetch_related("role")

    def get_extra_context(self, request, instance):
        services_table = ServiceTable(instance.services.all())
        services_table.configure(request)

        dataflows_table = tables.DataFlowTable(instance.dataflows.all())
        dataflows_table.configure(request)

        return {
            "services_table": services_table,
            "dataflows_table": dataflows_table,
        }


class ApplicationListView(generic.ObjectListView):
    queryset = models.Application.objects.annotate(
        service_count=Count("services", distinct=True),
        dataflow_count=Count("dataflows", distinct=True),
    )
    table = tables.ApplicationTable
    filterset = filtersets.ApplicationFilterSet
    filterset_form = forms.ApplicationFilterForm


class ApplicationEditView(generic.ObjectEditView):
    queryset = models.Application.objects.all()
    form = forms.ApplicationForm


class ApplicationDeleteView(generic.ObjectDeleteView):
    queryset = models.Application.objects.all()


class ApplicationBulkImportView(generic.BulkImportView):
    queryset = models.Application.objects.all()
    model_form = forms.ApplicationCSVForm
    table = tables.ApplicationTable


class ApplicationBulkEditView(generic.BulkEditView):
    queryset = models.Application.objects.prefetch_related("role").annotate(
        service_count=Count("services", distinct=True),
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable
    form = forms.ApplicationBulkEditForm


class ApplicationBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Application.objects.annotate(
        service_count=Count("services", distinct=True),
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable
