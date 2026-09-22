from django.db.models import Prefetch, Value

from netbox.views import generic
from utilities.views import ViewTab, register_model_view

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine

from netbox_data_flows import models, tables
from netbox_data_flows.choices import ObjectAliasMatchingChoices
from netbox_data_flows.utils.views import annotate_objectalias_counts

__all__ = tuple()


# NetBox models where we want to add a tab view
MODELS = (Device, VirtualMachine, IPAddress, IPRange, Prefix)


def _count_aliases_or_dataflows(obj):
    # We align with NetBox behaviour (e.g. ClusterVirtualMachinesView)
    # and count all objects, even those not visible by the user
    # i.e.: permissions are not applied

    aliases = models.ObjectAlias.objects.contains(obj).count()
    if not aliases:
        return 0  # cannot have a dataflow without an alias

    dataflows = models.DataFlow.objects.sources_or_destinations(obj).count()

    # return as string so "0" is considered non-empty
    # we display the object aliases even without a data flow
    return str(dataflows)


class DataFlowListTabViewBase(generic.ObjectView):
    """Add a tab with ObjectAlias and DataFlows to built-in models."""

    def __init_subclass__(cls, /, model, **kwargs):
        """Create a subclass associated to a NetBox model."""
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
    additional_permissions = ("netbox_data_flows.view_dataflow",)

    tab = ViewTab(
        label="Data Flows",
        permission="netbox_data_flows.view_dataflow",
        badge=_count_aliases_or_dataflows,
        hide_if_empty=True,
    )

    def get_extra_context(self, request, parent):
        DIRECT = Value(ObjectAliasMatchingChoices.MATCHING_DIRECT)
        INDIRECT = Value(ObjectAliasMatchingChoices.MATCHING_INDIRECT)
        TAGGED = Value(ObjectAliasMatchingChoices.MATCHING_TAGGED)

        # Apply permissions before every UNION branch; filtering a combined QuerySet is not supported.
        aliases = annotate_objectalias_counts(models.ObjectAlias.objects.restrict(request.user, "view"), request.user)
        dataflows = models.DataFlow.objects.restrict(request.user, "view")

        aliases_table = tables.SourcedObjectAliasTable(
            aliases.annotate(result_source=DIRECT)
            .contains(parent, direct=True)
            .union(aliases.annotate(result_source=TAGGED).contains(parent, tagged=True))
            .union(aliases.annotate(result_source=INDIRECT).contains(parent, indirect=True))
            .order_by(*(("result_source",) + models.ObjectAlias._meta.ordering))
        )
        aliases_table.configure(request)

        dataflow_sources_table = tables.SourcedDataFlowTable(
            dataflows.sources(parent, direct=True)
            .annotate(result_source=DIRECT)
            .prefetch_related(
                "application",
                "group",
                Prefetch("sources", queryset=models.ObjectAlias.objects.restrict(request.user, "view")),
                Prefetch("destinations", queryset=models.ObjectAlias.objects.restrict(request.user, "view")),
            )
            .union(dataflows.sources(parent, indirect=True).annotate(result_source=INDIRECT))
            .union(dataflows.sources(parent, tagged=True).annotate(result_source=TAGGED))
            .order_by(*(("result_source",) + models.DataFlow._meta.ordering))
        )
        dataflow_sources_table.configure(request)

        dataflow_destinations_table = tables.SourcedDataFlowTable(
            dataflows.destinations(parent, direct=True)
            .annotate(result_source=DIRECT)
            .prefetch_related(
                "application",
                "group",
                Prefetch("sources", queryset=models.ObjectAlias.objects.restrict(request.user, "view")),
                Prefetch("destinations", queryset=models.ObjectAlias.objects.restrict(request.user, "view")),
            )
            .union(dataflows.destinations(parent, indirect=True).annotate(result_source=INDIRECT))
            .union(dataflows.destinations(parent, tagged=True).annotate(result_source=TAGGED))
            .order_by(*(("result_source",) + models.DataFlow._meta.ordering))
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
