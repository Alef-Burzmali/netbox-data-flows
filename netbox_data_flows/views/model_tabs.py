from django.db.models import Count

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine

from netbox_data_flows import models, tables


__all__ = tuple()


# NetBox models where we want to add a tab view
MODELS = (Device, VirtualMachine, IPAddress, IPRange, Prefix)


def _count_related_aliases_or_dataflows(obj):
    aliases = models.ObjectAlias.objects.contains(obj).count()
    if not aliases:
        return 0  # cannot have a dataflow without an alias

    dataflows = models.DataFlow.objects.sources_or_destinations(obj).count()
    # return as string so "0" is considered non-empty
    return str(dataflows)


class DataFlowListTabViewBase(generic.ObjectView):
    """
    Add a tab with ObjectAlias and DataFlows to built-in
    models
    """

    def __init_subclass__(cls, /, model, **kwargs):
        """Create a subclass associated to a NetBox model"""

        super().__init_subclass__(**kwargs)

        # map the queryset to our NetBox model
        cls.queryset = model.objects.all()

        # call the decorator to register the view
        register_model_view(
            model,
            name="dataflows-tab",
            path="dataflows",
        )(cls)

    queryset = None
    template_name = "netbox_data_flows/dataflow_tab.html"
    actions = ("changelog",)

    tab = ViewTab(
        label="Data Flows",
        permission="netbox_data_flows.view_dataflow",
        badge=_count_related_aliases_or_dataflows,
        hide_if_empty=True,
    )

    def get_extra_context(self, request, parent):
        aliases_table = tables.ObjectAliasTable(
            models.ObjectAlias.objects.annotate(
                target_count=Count("targets", distinct=True),
            ).contains(parent)
        )
        aliases_table.configure(request)

        dataflow_sources_table = tables.DataFlowTable(
            models.DataFlow.objects.sources(parent).prefetch_related(
                "application",
                "application__role",
                "group",
                "sources",
                "destinations",
            )
        )
        dataflow_sources_table.configure(request)

        dataflow_destinations_table = tables.DataFlowTable(
            models.DataFlow.objects.destinations(parent).prefetch_related(
                "application",
                "application__role",
                "group",
                "sources",
                "destinations",
            )
        )
        dataflow_destinations_table.configure(request)

        return {
            "aliases_table": aliases_table,
            "dataflow_sources_table": dataflow_sources_table,
            "dataflow_destinations_table": dataflow_destinations_table,
        }


for model in MODELS:
    # create a subclass of DataFlowListTabViewBase per model
    type(
        f"{model.__name__}DataFlowTabView",
        (DataFlowListTabViewBase,),
        {},
        model=model,
    )
