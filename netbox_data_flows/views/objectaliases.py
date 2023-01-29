from django.db.models import Count

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine

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
    queryset = models.ObjectAlias.objects.annotate(
        target_count=Count("targets"),
    )
    table = tables.ObjectAliasTable
    filterset = filtersets.ObjectAliasFilterSet
    filterset_form = forms.ObjectAliasFilterForm


@register_model_view(models.ObjectAlias)
class ObjectAliasView(generic.ObjectView):
    queryset = models.ObjectAlias.objects.prefetch_related(
        "targets",
        "dataflow_sources",
        "dataflow_destinations",
    )

    def get_extra_context(self, request, instance):
        targets_table = tables.ObjectAliasTargetTable(
            instance.targets.all(), extra_context={"objectalias": instance}
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
    queryset = models.ObjectAlias.objects.all()
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
    form = forms.ObjectAliasBulkEditForm


class ObjectAliasBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ObjectAlias.objects.all()
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


#
# As tabs
#


class ObjectAliasListTabViewBase(generic.ObjectChildrenView):
    queryset = None
    child_model = models.ObjectAlias
    table = tables.ObjectAliasTable
    filterset = filtersets.ObjectAliasFilterSet
    template_name = "netbox_data_flows/objectalias_tab.html"
    actions = ("changelog",)

    tab = ViewTab(
        label="Object Aliases",
        permission="netbox_data_flows.view_objectalias",
        badge=lambda obj: models.ObjectAlias.objects.contains(obj).count(),
        hide_if_empty=True,
    )

    def get_children(self, request, parent):
        return models.ObjectAlias.objects.contains(parent).annotate(
            target_count=Count("targets"),
        )


@register_model_view(Device, name="objectalias-tab", path="aliases")
class DeviceObjectAliasListTabView(ObjectAliasListTabViewBase):
    queryset = Device.objects.all()


@register_model_view(VirtualMachine, name="objectalias-tab", path="aliases")
class VirtualMachineObjectAliasListTabView(ObjectAliasListTabViewBase):
    queryset = VirtualMachine.objects.all()


@register_model_view(IPAddress, name="objectalias-tab", path="aliases")
class VirtualMachineObjectAliasListTabView(ObjectAliasListTabViewBase):
    queryset = IPAddress.objects.all()


@register_model_view(IPRange, name="objectalias-tab", path="aliases")
class VirtualMachineObjectAliasListTabView(ObjectAliasListTabViewBase):
    queryset = IPRange.objects.all()


@register_model_view(Prefix, name="objectalias-tab", path="aliases")
class VirtualMachineObjectAliasListTabView(ObjectAliasListTabViewBase):
    queryset = Prefix.objects.all()
