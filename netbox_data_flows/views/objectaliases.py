from netbox.views import generic
from utilities.views import GetRelatedModelsMixin, ViewTab, register_model_view

from ipam.tables import IPAddressTable, IPRangeTable, PrefixTable

from netbox_data_flows import filtersets, forms, models, tables
from netbox_data_flows.utils.helpers import object_list_to_string
from netbox_data_flows.utils.views import annotate_objectalias_counts

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


class ObjectAliasTableMixin:
    """
    Annotate the Object Alias queryset with related object counts and re-apply ordering.

    Re-applying ordering is required due to the JOINs performed by annotate.
    """

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = annotate_objectalias_counts(queryset, request.user)
        return queryset.order_by(*models.ObjectAlias._meta.ordering)


@register_model_view(models.ObjectAlias, "list", path="", detail=False)
class ObjectAliasListView(ObjectAliasTableMixin, generic.ObjectListView):
    queryset = models.ObjectAlias.objects.all()
    table = tables.ObjectAliasTable
    filterset = filtersets.ObjectAliasFilterSet
    filterset_form = forms.ObjectAliasFilterForm


@register_model_view(models.ObjectAlias)
class ObjectAliasView(GetRelatedDataFlowsMixin, generic.ObjectView):
    queryset = models.ObjectAlias.objects.all()

    def get_extra_context(self, request, instance):
        related_models = self.get_related_models(request, instance)

        prefixes = instance.prefixes.restrict(request.user, "view")
        ip_ranges = instance.ip_ranges.restrict(request.user, "view")
        ip_addresses = instance.ip_addresses.restrict(request.user, "view")

        prefix_table = PrefixTable(prefixes)
        prefix_table.configure(request)

        ip_range_table = IPRangeTable(ip_ranges)
        ip_range_table.configure(request)

        ip_address_table = IPAddressTable(ip_addresses)
        ip_address_table.configure(request)

        resolved_ip_addresses = instance.get_resolved_ip_addresses(include_direct_assignments=False).restrict(
            request.user, "view"
        )
        resolved_ip_address_table = IPAddressTable(resolved_ip_addresses)
        resolved_ip_address_table.configure(request)

        return {
            "device_tags": object_list_to_string(instance.device_tags.all(), linkify=True),
            "related_models": related_models,
            "prefix_table": prefix_table,
            "prefix_count": prefixes.count(),
            "ip_range_table": ip_range_table,
            "ip_range_count": ip_ranges.count(),
            "ip_address_table": ip_address_table,
            "ip_address_count": ip_addresses.count(),
            "resolved_ip_address_count": resolved_ip_addresses.count(),
            "resolved_ip_address_table": resolved_ip_address_table,
            "virtual_machine_tags": object_list_to_string(instance.virtual_machine_tags.all(), linkify=True),
        }


@register_model_view(models.ObjectAlias, name="objectalias-dataflows-tab", path="dataflows")
class ObjectAliasDataFlowView(generic.ObjectView):
    queryset = models.ObjectAlias.objects.all()
    template_name = "netbox_data_flows/objectalias_dataflows.html"
    additional_permissions = ("netbox_data_flows.view_dataflow",)

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
class ObjectAliasBulkEditView(ObjectAliasTableMixin, generic.BulkEditView):
    queryset = models.ObjectAlias.objects.all()
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
    form = forms.ObjectAliasBulkEditForm


@register_model_view(models.ObjectAlias, "bulk_delete", path="delete", detail=False)
class ObjectAliasBulkDeleteView(ObjectAliasTableMixin, generic.BulkDeleteView):
    queryset = models.ObjectAlias.objects.all()
    filterset = filtersets.ObjectAliasFilterSet
    table = tables.ObjectAliasTable
