from netbox.graphql.types import NetBoxObjectType

from netbox_data_flows import filtersets, models


__all__ = (
    "ObjectAliasType",
    "ObjectAliasTargetType",
)


class ObjectAliasTargetType(NetBoxObjectType):
    class Meta:
        model = models.ObjectAliasTarget
        fields = "__all__"
        filterset_class = filtersets.ObjectAliasTargetFilterSet


class ObjectAliasType(NetBoxObjectType):
    class Meta:
        model = models.ObjectAlias
        fields = "__all__"
        filterset_class = filtersets.ObjectAliasFilterSet
