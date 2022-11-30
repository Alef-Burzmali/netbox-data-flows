import django_tables2 as tables

from netbox.tables import (
    columns,
    NetBoxTable,
)

from netbox_data_flows.models import ObjectAlias, ObjectAliasTarget


__all__ = (
    "ObjectAliasTable",
    "ObjectAliasTargetTable",
)


class ObjectAliasTargetTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    target = tables.Column(linkify=True, verbose_name="Object")
    parent = tables.Column(
        linkify=True,
        verbose_name="Device/VM or VLAN",
    )
    actions = None

    class Meta(NetBoxTable.Meta):
        model = ObjectAliasTarget
        fields = (
            "pk",
            "id",
            "name",
            "target",
            "parent",
            "size",
            "family",
            "created",
            "last_updated",
            # "actions",
        )
        default_columns = (
            "name",
            "target",
            "parent",
        )


class ObjectAliasTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
    )
    target_count = tables.Column(
        verbose_name="Aliased objects",
    )
    # dataflow_count = columns.LinkedCountColumn(
    #    viewname="plugins:netbox_data_flows:dataflow_list",
    #    url_params={"pk": "pk"},
    #    verbose_name="Objects",
    # )
    tags = columns.TagColumn(
        url_name="plugins:netbox_data_flows:objectalias_list"
    )

    class Meta(NetBoxTable.Meta):
        model = ObjectAlias
        fields = (
            "pk",
            "id",
            "name",
            "description",
            "size",
            "target_count",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "description",
            "target_count",
        )
