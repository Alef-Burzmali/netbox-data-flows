from netbox.graphql.types import NetBoxObjectType

from netbox_data_flows import filtersets, models


__all__ = ("DataFlowGroupType",)


class DataFlowGroupType(NetBoxObjectType):
    class Meta:
        model = models.DataFlowGroup
        fields = "__all__"
        filterset_class = filtersets.DataFlowGroupFilterSet
