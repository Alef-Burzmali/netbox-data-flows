from rest_framework import serializers

from netbox.api.fields import ChoiceField
from netbox.api.serializers import (
    NetBoxModelSerializer,
    WritableNestedSerializer,
)

from netbox_data_flows import models, choices

from .applications import ApplicationSerializer


__all__ = (
    "NestedDataFlowGroupSerializer",
    "DataFlowGroupSerializer",
)


class NestedDataFlowGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:dataflowgroup-detail"
    )

    status = ChoiceField(choices=choices.DataFlowStatusChoices, required=False)
    _depth = serializers.IntegerField(source="level", read_only=True)

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "slug",
            "status",
            "_depth",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "slug",
            "status",
            "_depth",
        )


class DataFlowGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:dataflowgroup-detail"
    )

    status = ChoiceField(choices=choices.DataFlowStatusChoices, required=False)
    inherited_status = ChoiceField(
        choices=choices.DataFlowInheritedStatusChoices,
        required=False,
        read_only=True,
    )

    application = ApplicationSerializer(
        nested=True, required=False, allow_null=True, default=None
    )
    parent = NestedDataFlowGroupSerializer(
        nested=True, required=False, allow_null=True, default=None
    )
    _depth = serializers.IntegerField(source="level", read_only=True)

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "id",
            "url",
            "display",
            "slug",
            "application",
            "parent",
            "name",
            "description",
            "status",
            "inherited_status",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "_depth",
        )
        brief_fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "slug",
            "status",
        )
