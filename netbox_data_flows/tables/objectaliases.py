import django_tables2 as tables

from netbox.tables import (
    columns,
    NetBoxTable,
)

from netbox_data_flows.models import ObjectAlias, ObjectAliasTarget
from netbox_data_flows.utils.tables import RuntimeTemplateColumn


__all__ = (
    "ObjectAliasTable",
    "ObjectAliasTargetTable",
)


class ObjectAliasTargetTable(NetBoxTable):
    extra_context = None

    type = tables.Column(
        accessor=tables.A("type_verbose_name"),
        order_by=tables.A("target_type"),
        verbose_name="Type",
    )
    name = tables.Column(
        linkify=True,
        orderable=False,
    )
    target = tables.Column(linkify=True, verbose_name="Object")
    parent = tables.Column(
        linkify=True,
        verbose_name="Device/VM or VLAN",
    )
    actions = RuntimeTemplateColumn(
        template_name="netbox_data_flows/inc/objectaliastarget_actions.html",
    )

    def __init__(self, *args, extra_context={}, **kwargs):
        self.extra_context = dict(extra_context)
        super().__init__(*args, **kwargs)

    class Meta(NetBoxTable.Meta):
        model = ObjectAliasTarget
        fields = (
            "pk",
            "id",
            "type",
            "name",
            "target",
            "parent",
            "family",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "type",
            "name",
            "parent",
            "actions",
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
