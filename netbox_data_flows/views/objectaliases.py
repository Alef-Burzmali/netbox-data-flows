from django.db.models import Count

from netbox.views import generic
from utilities.views import register_model_view

from netbox_data_flows import filtersets, forms, models, tables
from netbox_data_flows.utils.aliases import AddAliasesView, RemoveAliasView


__all__ = (
    "ObjectAliasView",
    "ObjectAliasListView",
    "ObjectAliasEditView",
    "ObjectAliasDeleteView",
    "ObjectAliasBulkImportView",
    "ObjectAliasBulkEditView",
    "ObjectAliasBulkDeleteView",
    "ObjectAliasAddTargetView",
    "ObjectAliasRemoveTargetView",
)


class ObjectAliasListView(generic.ObjectListView):
    queryset = models.ObjectAlias.objects.all().annotate(
        target_count=Count("targets", distinct=True),
    )
    table = tables.ObjectAliasTable
    filterset = filtersets.ObjectAliasFilterSet
    filterset_form = forms.ObjectAliasFilterForm


@register_model_view(models.ObjectAlias)
class ObjectAliasView(generic.ObjectView):
    queryset = models.ObjectAlias.objects.all()

    def get_extra_context(self, request, instance):
        targets_table = tables.ObjectAliasTargetTable(
            instance.targets.prefetch_related("target_type", "target"),
            extra_context={"objectalias": instance},
        )
        targets_table.configure(request)

        dataflow_sources_table = tables.DataFlowTable(
            instance.dataflow_sources.all()
        )
        dataflow_sources_table.configure(request)

        dataflow_destinations_table = tables.DataFlowTable(
            instance.dataflow_destinations.all()
        )
        dataflow_destinations_table.configure(request)

        return {
            "targets_table": targets_table,
            "dataflow_sources_table": dataflow_sources_table,
            "dataflow_destinations_table": dataflow_destinations_table,
        }


@register_model_view(models.ObjectAlias, "edit")
class ObjectAliasEditView(generic.ObjectEditView):
    queryset = models.ObjectAlias.objects.all()
    form = forms.ObjectAliasForm


@register_model_view(models.ObjectAlias, "delete")
class ObjectAliasDeleteView(generic.ObjectDeleteView):
    queryset = models.ObjectAlias.objects.all()


class ObjectAliasBulkImportView(generic.BulkImportView):
    queryset = models.ObjectAlias.objects.all()
    model_form = forms.ObjectAliasImportForm
    table = tables.ObjectAliasTable


class ObjectAliasBulkEditView(generic.BulkEditView):
    queryset = models.ObjectAlias.objects.annotate(
        target_count=Count("targets", distinct=True),
    )
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
    form = forms.ObjectAliasBulkEditForm


class ObjectAliasBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ObjectAlias.objects.annotate(
        target_count=Count("targets", distinct=True),
    )
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable


@register_model_view(models.ObjectAlias, name="addtarget", path="link")
class ObjectAliasAddTargetView(AddAliasesView):
    """Add ObjectAliasTarget(s) to an ObjectAlias"""

    queryset = models.ObjectAlias.objects.all()
    form = forms.ObjectAliasAddTargetForm
    alias_model = models.ObjectAliasTarget
    aliases_attribute = "targets"


@register_model_view(
    models.ObjectAlias, name="removetarget", path="unlink/<int:alias_pk>"
)
class ObjectAliasRemoveTargetView(RemoveAliasView):
    """Remove one ObjectAliasTarget from an ObjectAlias"""

    queryset = models.ObjectAlias.objects.all()
    aliases_attribute = "targets"
    template_name = "netbox_data_flows/objectalias_removetarget.html"
