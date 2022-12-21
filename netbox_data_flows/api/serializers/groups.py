from rest_framework import serializers

from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer

from netbox_data_flows import models, choices

from .nested import *


__all__ = ("DataFlowGroupSerializer",)


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

    application = NestedApplicationSerializer(
        required=False, allow_null=True, default=None
    )
    parent = NestedDataFlowGroupSerializer(
        required=False, allow_null=True, default=None
    )
    ancestor = NestedDataFlowGroupSerializer(
        required=False, allow_null=True, default=None
    )

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "id",
            "url",
            "display",
            "application",
            "parent",
            "ancestor",
            "name",
            "description",
            "status",
            "inherited_status",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
