import itertools

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine

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
        "application", "application__role", "group", "sources", "destinations"
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
        "sources__targets",
        "destinations__targets",
    )

    tab = ViewTab(
        label="Targets",
        permission="netbox_data_flows.view_dataflow",
        hide_if_empty=False,
    )

    def get_extra_context(self, request, instance):
        sources_targets = itertools.chain.from_iterable(
            alias.targets.all() for alias in instance.sources.all()
        )
        destinations_targets = itertools.chain.from_iterable(
            alias.targets.all() for alias in instance.destinations.all()
        )

        # Remove duplicates
        sources_targets = set(sources_targets)
        destinations_targets = set(destinations_targets)

        sources_table = tables.ObjectAliasTargetTable(
            sources_targets, extra_context={"objectalias": None}
        )
        destinations_table = tables.ObjectAliasTargetTable(
            destinations_targets, extra_context={"objectalias": None}
        )

        return {
            "sources_table": sources_table,
            "destinations_table": destinations_table,
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


#
# As tabs
#


class DataFlowListTabViewBase(generic.ObjectChildrenView):
    queryset = None
    child_model = models.DataFlow
    table = tables.DataFlowTable
    filterset = filtersets.DataFlowFilterSet
    template_name = "netbox_data_flows/dataflow_tab.html"
    actions = ("changelog",)

    tab = ViewTab(
        label="Data Flows",
        permission="netbox_data_flows.view_dataflow",
        badge=lambda obj: models.DataFlow.objects.source_or_destination(
            obj
        ).count(),
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return models.DataFlow.objects.source_or_destination(
            parent
        ).prefetch_related(
            "application",
            "application__role",
            "group",
        )


@register_model_view(Device, name="dataflows-tab", path="dataflows")
class DeviceDataFlowListTabView(DataFlowListTabViewBase):
    queryset = Device.objects.all()


@register_model_view(VirtualMachine, name="dataflows-tab", path="dataflows")
class VirtualMachineDataFlowListTabView(DataFlowListTabViewBase):
    queryset = VirtualMachine.objects.all()


@register_model_view(IPAddress, name="dataflows-tab", path="dataflows")
class IPAddressDataFlowListTabView(DataFlowListTabViewBase):
    queryset = IPAddress.objects.all()


@register_model_view(IPRange, name="dataflows-tab", path="dataflows")
class IPRangeDataFlowListTabView(DataFlowListTabViewBase):
    queryset = IPRange.objects.all()


@register_model_view(Prefix, name="dataflows-tab", path="dataflows")
class PrefixDataFlowListTabView(DataFlowListTabViewBase):
    queryset = Prefix.objects.all()
