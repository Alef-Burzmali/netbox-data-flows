from django.db.models import Count

from netbox.views import generic
from utilities.views import GetRelatedModelsMixin, ViewTab, register_model_view

from ipam.tables import IPAddressTable, IPRangeTable, PrefixTable

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


class GetRelatedDataFlowsMixin(GetRelatedModelsMixin):
    def get_related_models(self, request, instance, omit=tuple(), extra=tuple()):
        """
        Get related dataflows of an object alias based on their direction.

        Args:
            request: Current request being processed.
            instance: The instance related models should be looked up for.
            omit: Remove relationships to these models from the result. Needs to be passed, if related models don't
                provide a `_list` view.
            extra: Add extra models to the list of automatically determined related models. Can be used to add indirect
                relationships.
        """
        df = models.DataFlow.objects.restrict(request.user, "view")
        related_models = [
            (df.filter(sources__pk=instance.pk), "source_aliases", "Data Flows as Source"),
            (df.filter(destinations__pk=instance.pk), "destination_aliases", "Data Flows as Destination"),
        ]

        return super().get_related_models(request, instance, omit=omit, extra=related_models)


@register_model_view(models.ObjectAlias, "list", path="", detail=False)
class ObjectAliasListView(generic.ObjectListView):
    queryset = models.ObjectAlias.objects.annotate(
        prefix_count=Count("prefixes", distinct=True),
        ip_range_count=Count("ip_ranges", distinct=True),
        ip_address_count=Count("ip_addresses", distinct=True),
        dataflow_source_count=Count("dataflow_sources", distinct=True),
        dataflow_destination_count=Count("dataflow_destinations", distinct=True),
    ).order_by(*models.ObjectAlias._meta.ordering)
    table = tables.ObjectAliasTable
    filterset = filtersets.ObjectAliasFilterSet
    filterset_form = forms.ObjectAliasFilterForm


@register_model_view(models.ObjectAlias)
class ObjectAliasView(GetRelatedDataFlowsMixin, generic.ObjectView):
    queryset = models.ObjectAlias.objects.all()

    def get_extra_context(self, request, instance):
        related_models = self.get_related_models(request, instance)

        prefix_table = PrefixTable(instance.prefixes.all())
        prefix_table.configure(request)

        ip_range_table = IPRangeTable(instance.ip_ranges.all())
        ip_range_table.configure(request)

        ip_address_table = IPAddressTable(instance.ip_addresses.all())
        ip_address_table.configure(request)

        return {
            "related_models": related_models,
            "prefix_table": prefix_table,
            "ip_range_table": ip_range_table,
            "ip_address_table": ip_address_table,
        }


@register_model_view(models.ObjectAlias, name="objectalias-dataflows-tab", path="dataflows")
class ObjectAliasDataFlowView(generic.ObjectView):
    queryset = models.ObjectAlias.objects.all()
    template_name = "netbox_data_flows/objectalias_dataflows.html"

    tab = ViewTab(
        label="Data Flows",
        permission="netbox_data_flows.view_dataflow",
        badge=lambda o: o.dataflow_sources.count() + o.dataflow_destinations.count(),
        hide_if_empty=False,
    )


@register_model_view(models.ObjectAlias, "add", detail=False)
@register_model_view(models.ObjectAlias, "edit")
class ObjectAliasEditView(generic.ObjectEditView):
    queryset = models.ObjectAlias.objects.all()
    form = forms.ObjectAliasForm


@register_model_view(models.ObjectAlias, "delete")
class ObjectAliasDeleteView(generic.ObjectDeleteView):
    queryset = models.ObjectAlias.objects.all()


@register_model_view(models.ObjectAlias, "bulk_import", path="import", detail=False)
class ObjectAliasBulkImportView(generic.BulkImportView):
    queryset = models.ObjectAlias.objects.all()
    model_form = forms.ObjectAliasImportForm
    table = tables.ObjectAliasTable


@register_model_view(models.ObjectAlias, "bulk_edit", path="edit", detail=False)
class ObjectAliasBulkEditView(generic.BulkEditView):
    queryset = models.ObjectAlias.objects.annotate(
        prefix_count=Count("prefixes", distinct=True),
        ip_range_count=Count("ip_ranges", distinct=True),
        ip_address_count=Count("ip_addresses", distinct=True),
    ).order_by(*models.ObjectAlias._meta.ordering)
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
    form = forms.ObjectAliasBulkEditForm


@register_model_view(models.ObjectAlias, "bulk_delete", path="delete", detail=False)
class ObjectAliasBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ObjectAlias.objects.annotate(
        prefix_count=Count("prefixes", distinct=True),
        ip_range_count=Count("ip_ranges", distinct=True),
        ip_address_count=Count("ip_addresses", distinct=True),
    ).order_by(*models.ObjectAlias._meta.ordering)
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
