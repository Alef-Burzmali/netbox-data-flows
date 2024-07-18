from rest_framework import serializers

from netbox.api.fields import ChoiceField
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer

from netbox_data_flows import choices, models

from .applications import ApplicationSerializer


__all__ = (
    "NestedDataFlowGroupSerializer",
    "DataFlowGroupSerializer",
)


class NestedDataFlowGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_data_flows-api:dataflowgroup-detail")

    status = ChoiceField(choices=choices.DataFlowStatusChoices, required=False)
    _depth = serializers.IntegerField(source="level", read_only=True)

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "_depth",
            "description",
            "id",
            "name",
            "slug",
            "status",
            "url",
        )
        brief_fields = (
            "_depth",
            "description",
            "display",
            "id",
            "name",
            "slug",
            "status",
            "url",
        )


class DataFlowGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_data_flows-api:dataflowgroup-detail")

    status = ChoiceField(choices=choices.DataFlowStatusChoices, required=False)
    inherited_status = ChoiceField(
        choices=choices.DataFlowInheritedStatusChoices,
        required=False,
        read_only=True,
    )

    application = ApplicationSerializer(nested=True, required=False, allow_null=True, default=None)
    parent = NestedDataFlowGroupSerializer(nested=True, required=False, allow_null=True, default=None)
    _depth = serializers.IntegerField(source="level", read_only=True)

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "_depth",
            "application",
            "comments",
            "created",
            "custom_fields",
            "description",
            "display",
            "id",
            "inherited_status",
            "last_updated",
            "name",
            "parent",
            "slug",
            "status",
            "tags",
            "url",
        )
        brief_fields = (
            "description",
            "display",
            "id",
            "name",
            "slug",
            "status",
            "url",
        )
