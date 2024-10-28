from django.db.models import Count

from netbox.views import generic
from utilities.views import register_model_view

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


class ObjectAliasListView(generic.ObjectListView):
    queryset = models.ObjectAlias.objects.annotate(
        prefix_count=Count("prefixes", distinct=True),
        ip_range_count=Count("ip_ranges", distinct=True),
        ip_address_count=Count("ip_addresses", distinct=True),
    ).order_by(*models.ObjectAlias._meta.ordering)
    table = tables.ObjectAliasTable
    filterset = filtersets.ObjectAliasFilterSet
    filterset_form = forms.ObjectAliasFilterForm


@register_model_view(models.ObjectAlias)
class ObjectAliasView(generic.ObjectView):
    queryset = models.ObjectAlias.objects.all()

    def get_extra_context(self, request, instance):
        prefix_table = PrefixTable(instance.prefixes.all())
        prefix_table.configure(request)

        ip_range_table = IPRangeTable(instance.ip_ranges.all())
        ip_range_table.configure(request)

        ip_address_table = IPAddressTable(instance.ip_addresses.all())
        ip_address_table.configure(request)

        dataflow_sources_table = tables.DataFlowTable(instance.dataflow_sources.all())
        dataflow_sources_table.configure(request)

        dataflow_destinations_table = tables.DataFlowTable(instance.dataflow_destinations.all())
        dataflow_destinations_table.configure(request)

        return {
            "prefix_table": prefix_table,
            "ip_range_table": ip_range_table,
            "ip_address_table": ip_address_table,
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
        prefix_count=Count("prefixes", distinct=True),
        ip_range_count=Count("ip_ranges", distinct=True),
        ip_address_count=Count("ip_addresses", distinct=True),
    ).order_by(*models.ObjectAlias._meta.ordering)
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
    form = forms.ObjectAliasBulkEditForm


class ObjectAliasBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ObjectAlias.objects.annotate(
        prefix_count=Count("prefixes", distinct=True),
        ip_range_count=Count("ip_ranges", distinct=True),
        ip_address_count=Count("ip_addresses", distinct=True),
    ).order_by(*models.ObjectAlias._meta.ordering)
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
