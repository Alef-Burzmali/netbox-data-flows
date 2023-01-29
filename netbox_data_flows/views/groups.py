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


class DataFlowGroupListView(generic.ObjectListView):
    queryset = models.DataFlowGroup.objects.prefetch_related(
        "application",
        "application__role",
        "parent",
    ).annotate(
        dataflow_count=Count("dataflows"),
    )
    table = tables.DataFlowGroupTable
    filterset = filtersets.DataFlowGroupFilterSet
    filterset_form = forms.DataFlowGroupFilterForm


@register_model_view(models.DataFlowGroup)
class DataFlowGroupView(generic.ObjectView):
    queryset = models.DataFlowGroup.objects.prefetch_related(
        "application",
        "application__role",
        "parent",
        "dataflows",
    )

    def get_extra_context(self, request, instance):
        children_table = tables.DataFlowGroupTable(
            instance.get_descendants(include_self=False)
        )
        children_table.configure(request)

        dataflows_table = tables.DataFlowTable(instance.dataflows.all())
        dataflows_table.configure(request)

        dataflows_recursive_table = tables.DataFlowTable(
            models.DataFlow.objects.part_of_group_recursive(instance)
        )
        dataflows_recursive_table.configure(request)

        return {
            "children_table": children_table,
            "dataflows_table": dataflows_table,
            "dataflows_recursive_table": dataflows_recursive_table,
        }


@register_model_view(models.DataFlowGroup, "edit")
class DataFlowGroupEditView(generic.ObjectEditView):
    queryset = models.DataFlowGroup.objects.prefetch_related(
        "application",
        "application__role",
        "parent",
    )
    form = forms.DataFlowGroupForm


@register_model_view(models.DataFlowGroup, "delete")
class DataFlowGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.DataFlowGroup.objects.all()


class DataFlowGroupBulkImportView(generic.BulkImportView):
    queryset = models.DataFlowGroup.objects.all()
    model_form = forms.DataFlowGroupImportForm
    table = tables.DataFlowGroupTable


class DataFlowGroupBulkEditView(generic.BulkEditView):
    queryset = models.DataFlowGroup.objects.prefetch_related(
        "application",
        "application__role",
        "parent",
    ).annotate(
        dataflow_count=Count("dataflows"),
    )
    filterset = filtersets.DataFlowGroupFilterSet
    table = tables.DataFlowGroupTable
    form = forms.DataFlowGroupBulkEditForm


class DataFlowGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DataFlowGroup.objects.prefetch_related(
        "application",
        "application__role",
        "parent",
    ).annotate(
        dataflow_count=Count("dataflows"),
    )
    filterset = filtersets.DataFlowGroupFilterSet
    table = tables.DataFlowGroupTable
