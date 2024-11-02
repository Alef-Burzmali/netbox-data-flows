from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from ipam.models import IPAddress, IPRange, Prefix
from ipam.tables import IPAddressTable, IPRangeTable, PrefixTable

from netbox_data_flows import filtersets, forms, models, tables


__all__ = (
    "DataFlowView",
    "DataFlowListView",
    "DataFlowRuleListView",
    "DataFlowEditView",
    "DataFlowDeleteView",
    "DataFlowBulkImportView",
    "DataFlowBulkEditView",
    "DataFlowBulkDeleteView",
)


class DataFlowListView(generic.ObjectListView):
    queryset = models.DataFlow.objects.prefetch_related(
        "application",
        "application__role",
        "group",
        "sources",
        "destinations",
    )
    table = tables.DataFlowTable
    filterset = filtersets.DataFlowFilterSet
    filterset_form = forms.DataFlowFilterForm
    template_name = "netbox_data_flows/dataflow_list.html"

    def get_extra_context(self, request):
        return {
            "as_rules": False,
        }


class DataFlowRuleListView(DataFlowListView):
    def get_queryset(self, request):
        # only_enabled() breaks lazy queryset
        return self.queryset.only_enabled()

    def get_extra_context(self, request):
        return {
            "as_rules": True,
            "actions": ("export",),
        }


@register_model_view(models.DataFlow)
class DataFlowView(generic.ObjectView):
    queryset = models.DataFlow.objects.prefetch_related(
        "application",
        "application__role",
        "group",
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
    queryset = models.DataFlow.objects.prefetch_related(
        "application",
        "sources",
        "destinations",
    )

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


@register_model_view(models.DataFlow, "edit")
class DataFlowEditView(generic.ObjectEditView):
    queryset = models.DataFlow.objects.all()
    form = forms.DataFlowForm


@register_model_view(models.DataFlow, "delete")
class DataFlowDeleteView(generic.ObjectDeleteView):
    queryset = models.DataFlow.objects.all()


class DataFlowBulkImportView(generic.BulkImportView):
    queryset = models.DataFlow.objects.all()
    model_form = forms.DataFlowImportForm
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
