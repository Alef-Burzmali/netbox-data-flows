import django_tables2 as tables

from netbox.tables import ChoiceFieldColumn, PrimaryModelTable, columns

from tenancy.tables import TenancyColumnsMixin

from netbox_data_flows import choices
from netbox_data_flows.models import DataFlow

from .columns import ChoiceVirtualColumn, ObjectAliasListColumn, PortListColumn

__all__ = (
    "DataFlowTable",
    "SourcedDataFlowTable",
)


class DataFlowTable(TenancyColumnsMixin, PrimaryModelTable):
    application = tables.Column(
        linkify=True,
    )
    application_role = tables.Column(
        linkify=True,
        accessor=tables.A("application__role"),
    )
    group = tables.Column(
        linkify=True,
    )
    name = columns.MPTTColumn(
        linkify=True,
    )
    status = ChoiceFieldColumn(accessor=tables.A("inherited_status_display"))
    protocol = ChoiceFieldColumn()

    source_ports = PortListColumn()
    destination_ports = PortListColumn()
    sources = ObjectAliasListColumn(
        orderable=False,
    )
    destinations = ObjectAliasListColumn(
        orderable=False,
    )

    tags = columns.TagColumn(url_name="plugins:netbox_data_flows:dataflow_list")

    class Meta(PrimaryModelTable.Meta):
        model = DataFlow
        fields = (
            "pk",
            "id",
            "application",
            "application_role",
            "group",
            "name",
            "description",
            "status",
            "protocol",
            "sources",
            "source_ports",
            "destinations",
            "destination_ports",
            "parent",
            "tenant",
            "tenant_group",
            "comments",
            "tags",
            "owner",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "application",
            "group",
            "name",
            "status",
            "protocol",
            "sources",
            "source_ports",
            "destinations",
            "destination_ports",
            "description",
        )


class SourcedDataFlowTable(DataFlowTable):
    result_source = ChoiceVirtualColumn(
        verbose_name="Assignment",
        choices=choices.ObjectAliasMatchingChoices,
    )

    class Meta(DataFlowTable.Meta):
        fields = (
            "pk",
            "id",
            "result_source",
            "application",
            "application_role",
            "group",
            "name",
            "description",
            "status",
            "protocol",
            "sources",
            "source_ports",
            "destinations",
            "destination_ports",
            "parent",
            "tenant",
            "tenant_group",
            "comments",
            "tags",
            "owner",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "result_source",
            "application",
            "group",
            "name",
            "status",
            "protocol",
            "sources",
            "source_ports",
            "destinations",
            "destination_ports",
            "description",
        )

    def _apply_prefetching(self, *args, **kwargs):
        # Disable NetBox's smart prefetching as it is not compatible with UNION
        # The UNION is used to merge the different querysets from the different sources.
        pass
