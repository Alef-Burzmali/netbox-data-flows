from django.db.models import Count

from netbox.views import generic
from utilities.views import register_model_view

from netbox_data_flows import filtersets, forms, models, tables


__all__ = (
    "DataFlowGroupView",
    "DataFlowGroupListView",
    "DataFlowGroupEditView",
    "DataFlowGroupDeleteView",
    "DataFlowGroupBulkImportView",
    "DataFlowGroupBulkEditView",
    "DataFlowGroupBulkDeleteView",
)


@register_model_view(models.DataFlowGroup, "list", path="", detail=False)
class DataFlowGroupListView(generic.ObjectListView):
    queryset = models.DataFlowGroup.objects.annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    table = tables.DataFlowGroupTable
    filterset = filtersets.DataFlowGroupFilterSet
    filterset_form = forms.DataFlowGroupFilterForm


@register_model_view(models.DataFlowGroup)
class DataFlowGroupView(generic.ObjectView):
    queryset = models.DataFlowGroup.objects.all()


@register_model_view(models.DataFlowGroup, "add", detail=False)
@register_model_view(models.DataFlowGroup, "edit")
class DataFlowGroupEditView(generic.ObjectEditView):
    queryset = models.DataFlowGroup.objects.all()
    form = forms.DataFlowGroupForm


@register_model_view(models.DataFlowGroup, "delete")
class DataFlowGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.DataFlowGroup.objects.all()


@register_model_view(models.DataFlowGroup, "bulk_import", path="import", detail=False)
class DataFlowGroupBulkImportView(generic.BulkImportView):
    queryset = models.DataFlowGroup.objects.all()
    model_form = forms.DataFlowGroupImportForm
    table = tables.DataFlowGroupTable


@register_model_view(models.DataFlowGroup, "bulk_edit", path="edit", detail=False)
class DataFlowGroupBulkEditView(generic.BulkEditView):
    queryset = models.DataFlowGroup.objects.annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.DataFlowGroupFilterSet
    table = tables.DataFlowGroupTable
    form = forms.DataFlowGroupBulkEditForm


@register_model_view(models.DataFlowGroup, "bulk_delete", path="delete", detail=False)
class DataFlowGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DataFlowGroup.objects.annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.DataFlowGroupFilterSet
    table = tables.DataFlowGroupTable
