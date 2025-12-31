import django_tables2 as tables

from netbox.tables import ChoiceFieldColumn, NestedGroupModelTable, columns

from tenancy.tables import TenancyColumnsMixin

from netbox_data_flows.models import DataFlowGroup


__all__ = ("DataFlowGroupTable",)


class DataFlowGroupTable(TenancyColumnsMixin, NestedGroupModelTable):
    application = tables.Column(
        linkify=True,
    )

    application_role = tables.Column(
        linkify=True,
        accessor=tables.A("application__role"),
    )

    status = ChoiceFieldColumn(accessor=tables.A("inherited_status_display"))

    dataflow_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_data_flows:dataflow_list",
        url_params={"dataflowgroup_id": "pk"},
        verbose_name="Data Flows",
    )

    tags = columns.TagColumn(url_name="plugins:netbox_data_flows:dataflowgroup_list")

    class Meta(NestedGroupModelTable.Meta):
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
            "name",
            "status",
            "application",
            "application_role",
            "dataflow_count",
        )
