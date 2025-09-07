from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ipam.models import IPAddress, IPRange, Prefix
from ipam.tables import IPAddressTable, IPRangeTable, PrefixTable

from netbox_data_flows import filtersets, forms, models, tables


__all__ = (
    "DataFlowView",
    "DataFlowListView",
    "DataFlowEditView",
    "DataFlowDeleteView",
    "DataFlowBulkImportView",
    "DataFlowBulkEditView",
    "DataFlowBulkDeleteView",
)


@register_model_view(models.DataFlow, "list", path="", detail=False)
class DataFlowListView(generic.ObjectListView):
    queryset = models.DataFlow.objects.all()
    table = tables.DataFlowTable
    filterset = filtersets.DataFlowFilterSet
    filterset_form = forms.DataFlowFilterForm


@register_model_view(models.DataFlow)
class DataFlowView(generic.ObjectView):
    queryset = models.DataFlow.objects.prefetch_related(
        "sources",
        "destinations",
    )

    def get_extra_context(self, request, instance):
        return {
            "sources": instance.sources.all(),
            "destinations": instance.destinations.all(),
        }


@register_model_view(models.DataFlow, "targets")
class DataFlowTargetView(generic.ObjectView):
    template_name = "netbox_data_flows/dataflow_targets.html"
    queryset = models.DataFlow.objects.all()

    tab = ViewTab(
        label="Targets",
        permission="netbox_data_flows.view_dataflow",
        hide_if_empty=False,
    )

    def get_extra_context(self, request, instance):
        # Get all unique sources and destinations
        # They could be duplicated if several ObjectAliases refer to them
        sources_prefixes = Prefix.objects.filter(data_flow_object_aliases__in=instance.sources.all()).distinct()
        sources_ip_ranges = IPRange.objects.filter(data_flow_object_aliases__in=instance.sources.all()).distinct()
        sources_ip_addresses = IPAddress.objects.filter(data_flow_object_aliases__in=instance.sources.all()).distinct()

        destinations_prefixes = Prefix.objects.filter(
            data_flow_object_aliases__in=instance.destinations.all()
        ).distinct()
        destinations_ip_ranges = IPRange.objects.filter(
            data_flow_object_aliases__in=instance.destinations.all()
        ).distinct()
        destinations_ip_addresses = IPAddress.objects.filter(
            data_flow_object_aliases__in=instance.destinations.all()
        ).distinct()

        # Prepare tables
        sources_prefixes_table = PrefixTable(sources_prefixes, orderable=False)
        sources_ip_ranges_table = IPRangeTable(sources_ip_ranges, orderable=False)
        sources_ip_addresses_table = IPAddressTable(sources_ip_addresses, orderable=False)

        destinations_prefixes_table = PrefixTable(destinations_prefixes, orderable=False)
        destinations_ip_ranges_table = IPRangeTable(destinations_ip_ranges, orderable=False)
        destinations_ip_addresses_table = IPAddressTable(destinations_ip_addresses, orderable=False)

        return {
            "sources_prefixes_table": sources_prefixes_table,
            "sources_ip_ranges_table": sources_ip_ranges_table,
            "sources_ip_addresses_table": sources_ip_addresses_table,
            "destinations_prefixes_table": destinations_prefixes_table,
            "destinations_ip_ranges_table": destinations_ip_ranges_table,
            "destinations_ip_addresses_table": destinations_ip_addresses_table,
        }


@register_model_view(models.DataFlow, "add", detail=False)
@register_model_view(models.DataFlow, "edit")
class DataFlowEditView(generic.ObjectEditView):
    queryset = models.DataFlow.objects.all()
    form = forms.DataFlowForm
    template_name = "netbox_data_flows/dataflow_edit.html"


@register_model_view(models.DataFlow, "delete")
class DataFlowDeleteView(generic.ObjectDeleteView):
    queryset = models.DataFlow.objects.all()


@register_model_view(models.DataFlow, "bulk_import", path="import", detail=False)
class DataFlowBulkImportView(generic.BulkImportView):
    queryset = models.DataFlow.objects.all()
    model_form = forms.DataFlowImportForm
    table = tables.DataFlowTable


@register_model_view(models.DataFlow, "bulk_edit", path="edit", detail=False)
class DataFlowBulkEditView(generic.BulkEditView):
    queryset = models.DataFlow.objects.all()
    filterset = filtersets.DataFlowFilterSet
    table = tables.DataFlowTable
    form = forms.DataFlowBulkEditForm


@register_model_view(models.DataFlow, "bulk_delete", path="delete", detail=False)
class DataFlowBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DataFlow.objects.all()
    filterset = filtersets.DataFlowFilterSet
    table = tables.DataFlowTable
