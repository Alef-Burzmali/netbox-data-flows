from netbox.graphql.types import NetBoxObjectType

from netbox_data_flows import filtersets, models


__all__ = ("DataFlowType",)


class DataFlowType(NetBoxObjectType):
    class Meta:
        model = models.DataFlow
        fields = "__all__"
        filterset_class = filtersets.DataFlowFilterSet
