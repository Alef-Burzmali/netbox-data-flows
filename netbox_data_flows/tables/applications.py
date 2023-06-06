import django_tables2 as tables

from netbox.tables import (
    columns,
    NetBoxTable,
)
from tenancy.tables import ContactsColumnMixin

from netbox_data_flows.models import Application, ApplicationRole


__all__ = (
    "ApplicationRoleTable",
    "ApplicationTable",
)


class ApplicationRoleTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    application_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_data_flows:application_list",
        url_params={"role_id": "pk"},
        verbose_name="Applications",
    )
    tags = columns.TagColumn(
        url_name="plugins:netbox_data_flows:applicationrole_list"
    )

    class Meta(NetBoxTable.Meta):
        model = ApplicationRole
        fields = (
            "pk",
            "id",
            "name",
            "slug",
            "application_count",
            "description",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = ("name", "description", "application_count")


class ApplicationTable(ContactsColumnMixin, NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    role = tables.Column(
        linkify=True,
    )
    dataflow_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_data_flows:dataflow_list",
        url_params={"application_id": "pk"},
        verbose_name="Data Flows",
    )
    tags = columns.TagColumn(
        url_name="plugins:netbox_data_flows:application_list"
    )

    class Meta(NetBoxTable.Meta):
        model = Application
        fields = (
            "pk",
            "id",
            "name",
            "description",
            "role",
            "contacts",
            "comments",
            "dataflow_count",
            "contacts",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = ("name", "role", "dataflow_count")
