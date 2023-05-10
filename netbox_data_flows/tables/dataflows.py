import django_tables2 as tables

from netbox.tables import (
    ChoiceFieldColumn,
    columns,
    NetBoxTable,
)

from netbox_data_flows.models import DataFlow


__all__ = (
    "DataFlowTable",
    "DataFlowRuleTable",
)


class DataFlowTable(NetBoxTable):
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

    source_ports = tables.Column(
        accessor=tables.A("source_port_list"),
        order_by=tables.A("source_ports"),
    )
    destination_ports = tables.Column(
        accessor=tables.A("destination_port_list"),
        order_by=tables.A("destination_ports"),
    )
    sources = tables.Column(
        accessor=tables.A("source_list"),
        orderable=False,
    )
    destinations = tables.Column(
        accessor=tables.A("destination_list"),
        orderable=False,
    )

    tags = columns.TagColumn(
        url_name="plugins:netbox_data_flows:dataflow_list"
    )

    class Meta(NetBoxTable.Meta):
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
            "depth",
            "comments",
            "tags",
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


class DataFlowRuleTable(NetBoxTable):
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

    source_ports = tables.Column(
        accessor=tables.A("source_port_list"),
        order_by=tables.A("source_ports"),
    )
    destination_ports = tables.Column(
        accessor=tables.A("destination_port_list"),
        order_by=tables.A("destination_ports"),
    )
    sources = tables.Column(
        accessor=tables.A("source_list"),
        orderable=False,
    )
    destinations = tables.Column(
        accessor=tables.A("destination_list"),
        orderable=False,
    )
    tags = columns.TagColumn(
        url_name="plugins:netbox_data_flows:dataflow_rules"
    )

    class Meta(NetBoxTable.Meta):
        model = DataFlow
        fields = (
            "pk",
            "id",
            "description",
            "application",
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
            "depth",
            "comments",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "protocol",
            "sources",
            "source_ports",
            "destinations",
            "destination_ports",
            "description",
        )
