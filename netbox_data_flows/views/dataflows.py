from netbox.views import generic

from netbox_data_flows import filtersets, forms, models, tables


__all__ = (
    "DataFlowView",
    "DataFlowListView",
    "DataFlowEditView",
    "DataFlowDeleteView",
    "DataFlowBulkImportView",
    "DataFlowBulkEditView",
    "DataFlowBulkDeleteView",
    "DataFlowRuleListView",
)


class DataFlowView(generic.ObjectView):
    queryset = models.DataFlow.objects.prefetch_related("application")

    def get_extra_context(self, request, instance):
        children_table = tables.DataFlowTable(
            instance.get_descendants(include_self=False)
        )
        children_table.configure(request)

        return {
            "children_table": children_table,
        }


class DataFlowListView(generic.ObjectListView):
    queryset = models.DataFlow.objects.prefetch_related(
        "application", "application__role"
    )
    table = tables.DataFlowTable
    filterset = filtersets.DataFlowFilterSet
    filterset_form = forms.DataFlowFilterForm
    template_name = "netbox_data_flows/dataflow_list.html"

    def get_extra_context(self, request):
        return {
            "as_rules": False,
        }


class DataFlowEditView(generic.ObjectEditView):
    queryset = models.DataFlow.objects.all()
    form = forms.DataFlowForm
    template_name = "netbox_data_flows/dataflow_edit.html"


class DataFlowDeleteView(generic.ObjectDeleteView):
    queryset = models.DataFlow.objects.all()


class DataFlowBulkImportView(generic.BulkImportView):
    queryset = models.DataFlow.objects.all()
    model_form = forms.DataFlowCSVForm
    table = tables.DataFlowTable


class DataFlowBulkEditView(generic.BulkEditView):
    queryset = models.DataFlow.objects.all()
    filterset = filtersets.DataFlowFilterSet
    table = tables.DataFlowTable
    form = forms.DataFlowBulkEditForm


class DataFlowBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DataFlow.objects.all()
    filterset = filtersets.DataFlowFilterSet
    table = tables.DataFlowTable


#
# As rule
#


class DataFlowRuleListView(generic.ObjectListView):
    queryset = models.DataFlow.objects.exclude(protocol="")
    table = tables.DataFlowRuleTable
    filterset = filtersets.DataFlowFilterSet
    filterset_form = forms.DataFlowFilterForm
    template_name = "netbox_data_flows/dataflow_list.html"

    def get_extra_context(self, request):
        return {
            "as_rules": True,
            "actions": ("export",),
        }
