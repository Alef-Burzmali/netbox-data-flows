from rest_framework import serializers

from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer

from netbox_data_flows import choices, models

from .applications import ApplicationSerializer
from .groups import DataFlowGroupSerializer
from .objectaliases import ObjectAliasSerializer


__all__ = ("DataFlowSerializer",)


class DataFlowSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_data_flows-api:dataflow-detail")

    application = ApplicationSerializer(nested=True, required=False, allow_null=True, default=None)
    group = DataFlowGroupSerializer(nested=True, required=False, allow_null=True, default=None)

    status = ChoiceField(choices=choices.DataFlowStatusChoices, required=False)
    inherited_status = ChoiceField(
        choices=choices.DataFlowInheritedStatusChoices,
        required=False,
        read_only=True,
    )
    protocol = ChoiceField(choices=choices.DataFlowProtocolChoices, required=False)

    sources = SerializedPKRelatedField(
        queryset=models.ObjectAlias.objects.all(),
        serializer=ObjectAliasSerializer,
        nested=True,
        required=False,
        many=True,
    )
    destinations = SerializedPKRelatedField(
        queryset=models.ObjectAlias.objects.all(),
        serializer=ObjectAliasSerializer,
        nested=True,
        required=False,
        many=True,
    )

    class Meta:
        model = models.DataFlow
        fields = (
            "application",
            "comments",
            "created",
            "custom_fields",
            "description",
            "destination_ports",
            "destinations",
            "display",
            "group",
            "id",
            "inherited_status",
            "last_updated",
            "name",
            "protocol",
            "source_ports",
            "sources",
            "status",
            "tags",
            "url",
        )
        brief_fields = (
            "description",
            "display",
            "id",
            "name",
            "url",
        )
