from rest_framework import serializers

from netbox.api.fields import ChoiceField
from netbox.api.serializers import NetBoxModelSerializer

from netbox_data_flows import models, choices

from . import nested


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

    application = nested.NestedApplicationSerializer(
        required=False, allow_null=True, default=None
    )
    parent = nested.NestedDataFlowGroupSerializer(
        required=False, allow_null=True, default=None
    )
    ancestor = nested.NestedDataFlowGroupSerializer(
        required=False, allow_null=True, default=None
    )

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "id",
            "url",
            "display",
            "slug",
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
