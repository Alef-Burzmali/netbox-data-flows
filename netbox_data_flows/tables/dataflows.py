import django_tables2 as tables

from netbox.tables import (
    ChoiceFieldColumn,
    columns,
    NetBoxTable,
)

from netbox_data_flows.models import DataFlow, DataFlowTemplate


__all__ = (
    "DataFlowTable",
    "DataFlowTemplateTable",
    "DataFlowRuleTable",
)


class DataFlowTemplateTable(NetBoxTable):
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
    source = tables.Column(
        linkify=True,
        order_by=(
            "source_device",
            "source_virtual_machine",
            "source_prefix",
            "source_ipaddress",
        ),
    )
    destination = tables.Column(
        linkify=True,
        order_by=(
            "destination_device",
            "destination_virtual_machine",
            "destination_prefix",
            "destination_ipaddress",
        ),
    )

    tags = columns.TagColumn(
        url_name="plugins:netbox_data_flows:dataflowtemplate_list"
    )

    class Meta(NetBoxTable.Meta):
        model = DataFlowTemplate
        fields = (
            "pk",
            "id",
            "name",
            "status",
            "protocol",
            "source",
            "source_ports",
            "destination",
            "destination_ports",
            "parent",
            "depth",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "status",
            "protocol",
            "source",
            "source_ports",
            "destination",
            "destination_ports",
        )


class DataFlowTable(NetBoxTable):
    application = tables.Column(
        linkify=True,
    )
    application_role = tables.Column(
        linkify=True,
        accessor=tables.A("application__role"),
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
    source = tables.Column(
        linkify=True,
        order_by=(
            "source_device",
            "source_virtual_machine",
            "source_prefix",
            "source_ipaddress",
        ),
    )
    destination = tables.Column(
        linkify=True,
        order_by=(
            "destination_device",
            "destination_virtual_machine",
            "destination_prefix",
            "destination_ipaddress",
        ),
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
            "name",
            "status",
            "protocol",
            "source",
            "source_ports",
            "destination",
            "destination_ports",
            "parent",
            "depth",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "application",
            "name",
            "status",
            "protocol",
            "source",
            "source_ports",
            "destination",
            "destination_ports",
        )


class DataFlowRuleTable(NetBoxTable):
    description = tables.Column(
        linkify=True,
    )
    application = tables.Column(
        linkify=True,
    )
    application_role = tables.Column(
        linkify=True,
        accessor=tables.A("application__role"),
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
    source = tables.Column(
        linkify=True,
        order_by=(
            "source_device",
            "source_virtual_machine",
            "source_prefix",
            "source_ipaddress",
        ),
    )
    destination = tables.Column(
        linkify=True,
        order_by=(
            "destination_device",
            "destination_virtual_machine",
            "destination_prefix",
            "destination_ipaddress",
        ),
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
            "name",
            "status",
            "protocol",
            "source",
            "source_ports",
            "destination",
            "destination_ports",
            "parent",
            "depth",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "protocol",
            "source",
            "source_ports",
            "destination",
            "destination_ports",
            "description",
        )
