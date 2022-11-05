from netbox.graphql.types import NetBoxObjectType

from netbox_data_flows import filtersets, models


__all__ = (
    "ApplicationType",
    "ApplicationRoleType",
)


class ApplicationRoleType(NetBoxObjectType):
    class Meta:
        model = models.ApplicationRole
        fields = "__all__"
        filterset_class = filtersets.ApplicationRoleFilterSet


class ApplicationType(NetBoxObjectType):
    class Meta:
        model = models.Application
        fields = "__all__"
        filterset_class = filtersets.ApplicationFilterSet
