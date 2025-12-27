import django_tables2 as tables

from netbox.tables import NetBoxTable, columns

from netbox_data_flows.models import ObjectAlias


__all__ = ("ObjectAliasTable",)


class ObjectAliasTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    prefix_count = tables.Column(
        verbose_name="Prefixes",
    )
    ip_range_count = tables.Column(
        verbose_name="IP Ranges",
    )
    ip_address_count = tables.Column(
        verbose_name="IP Addresses",
    )
    dataflow_source_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_data_flows:dataflow_list",
        url_params={"source_aliases": "pk"},
        verbose_name="Source in Dataflows",
    )
    dataflow_destination_count = columns.LinkedCountColumn(
        viewname="plugins:netbox_data_flows:dataflow_list",
        url_params={"destination_aliases": "pk"},
        verbose_name="Destination in Dataflows",
    )
    tags = columns.TagColumn(url_name="plugins:netbox_data_flows:objectalias_list")

    class Meta(NetBoxTable.Meta):
        model = ObjectAlias
        fields = (
            "pk",
            "id",
            "name",
            "description",
            "prefix_count",
            "ip_range_count",
            "ip_address_count",
            "dataflow_source_count",
            "dataflow_destination_count",
            "comments",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "description",
            "prefix_count",
            "ip_range_count",
            "ip_address_count",
            "dataflow_source_count",
            "dataflow_destination_count",
        )
