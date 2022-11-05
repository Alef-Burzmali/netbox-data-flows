from netbox.views import generic

from netbox_data_flows import filtersets, forms, models, tables


__all__ = (
    "DataFlowTemplateView",
    "DataFlowTemplateListView",
    "DataFlowTemplateEditView",
    "DataFlowTemplateDeleteView",
    "DataFlowTemplateBulkImportView",
    "DataFlowTemplateBulkEditView",
    "DataFlowTemplateBulkDeleteView",
)


class DataFlowTemplateView(generic.ObjectView):
    queryset = models.DataFlowTemplate.objects.all()

    def get_extra_context(self, request, instance):
        children_table = tables.DataFlowTemplateTable(
            instance.get_descendants(include_self=False)
        )
        children_table.configure(request)

        return {
            "children_table": children_table,
        }


class DataFlowTemplateListView(generic.ObjectListView):
    queryset = models.DataFlowTemplate.objects.all()
    table = tables.DataFlowTemplateTable
    filterset = filtersets.DataFlowTemplateFilterSet
    filterset_form = forms.DataFlowTemplateFilterForm


class DataFlowTemplateEditView(generic.ObjectEditView):
    queryset = models.DataFlowTemplate.objects.all()
    form = forms.DataFlowTemplateForm
    template_name = "netbox_data_flows/dataflow_edit.html"


class DataFlowTemplateDeleteView(generic.ObjectDeleteView):
    queryset = models.DataFlowTemplate.objects.all()


class DataFlowTemplateBulkImportView(generic.BulkImportView):
    queryset = models.DataFlowTemplate.objects.all()
    model_form = forms.DataFlowTemplateCSVForm
    table = tables.DataFlowTemplateTable


class DataFlowTemplateBulkEditView(generic.BulkEditView):
    queryset = models.DataFlowTemplate.objects.all()
    filterset = filtersets.DataFlowTemplateFilterSet
    table = tables.DataFlowTemplateTable
    form = forms.DataFlowTemplateBulkEditForm


class DataFlowTemplateBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DataFlowTemplate.objects.all()
    filterset = filtersets.DataFlowTemplateFilterSet
    table = tables.DataFlowTemplateTable
