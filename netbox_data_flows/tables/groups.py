import django_tables2 as tables

from netbox.tables import (
    ChoiceFieldColumn,
    columns,
    NetBoxTable,
)

from netbox_data_flows.models import DataFlowGroup


__all__ = ("DataFlowGroupTable",)


class DataFlowGroupTable(NetBoxTable):
    application = tables.Column(
        linkify=True,
    )

    application_role = tables.Column(
        linkify=True,
        accessor=tables.A("application__role"),
    )

    parent = tables.Column(
        linkify=True,
    )

    name = columns.MPTTColumn(
        linkify=True,
    )

    status = ChoiceFieldColumn(accessor=tables.A("inherited_status_display"))

    dataflow_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_data_flows:dataflow_list",
        url_params={"dataflowgroup_id": "pk"},
        verbose_name="Data Flows",
    )

    tags = columns.TagColumn(
        url_name="plugins:netbox_data_flows:dataflowgroup_list"
    )

    class Meta(NetBoxTable.Meta):
        model = DataFlowGroup
        fields = (
            "pk",
            "id",
            "name",
            "slug",
            "description",
            "status",
            "application",
            "application_role",
            "parent",
            "dataflow_count",
            "comments",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "application",
            "application_role",
            "dataflow_count",
        )
