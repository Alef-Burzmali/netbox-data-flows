from django.db.models import Count

from netbox.views import generic

from netbox_data_flows import filtersets, forms, models, tables


__all__ = (
    "ObjectAliasView",
    "ObjectAliasListView",
    "ObjectAliasEditView",
    "ObjectAliasDeleteView",
    "ObjectAliasBulkImportView",
    "ObjectAliasBulkEditView",
    "ObjectAliasBulkDeleteView",
)


class ObjectAliasView(generic.ObjectView):
    queryset = models.ObjectAlias.objects.all()

    def get_extra_context(self, request, instance):
        targets_table = tables.ObjectAliasTargetTable(instance.targets.all())
        targets_table.configure(request)

        # dataflows_table = tables.DataFlowTable(
        #    instance.dataflows.all()
        # )
        # dataflows_table.configure(request)

        return {
            "targets_table": targets_table,
            # "dataflows_table": dataflows_table,
        }


class ObjectAliasListView(generic.ObjectListView):
    queryset = models.ObjectAlias.objects.annotate(
        target_count=Count("targets"),
    )
    table = tables.ObjectAliasTable
    filterset = filtersets.ObjectAliasFilterSet


class ObjectAliasEditView(generic.ObjectEditView):
    queryset = models.ObjectAlias.objects.all()
    form = forms.ObjectAliasForm


class ObjectAliasDeleteView(generic.ObjectDeleteView):
    queryset = models.ObjectAlias.objects.all()


class ObjectAliasBulkImportView(generic.BulkImportView):
    queryset = models.ObjectAlias.objects.all()
    model_form = forms.ObjectAliasCSVForm
    table = tables.ObjectAliasTable


class ObjectAliasBulkEditView(generic.BulkEditView):
    queryset = models.ObjectAlias.objects.all()
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
    form = forms.ObjectAliasBulkEditForm


class ObjectAliasBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ObjectAlias.objects.all()
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
