from rest_framework import serializers

from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import (
    NetBoxModelSerializer,
    GenericObjectSerializer,
)

from netbox_data_flows import models


__all__ = (
    "ObjectAliasTargetSerializer",
    "ObjectAliasSerializer",
)


class ObjectAliasTargetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:objectaliastarget-detail"
    )
    target = GenericObjectSerializer(
        required=True,
        many=False,
    )

    class Meta:
        model = models.ObjectAliasTarget
        fields = (
            "id",
            "url",
            "display",
            "target",
        )


class ObjectAliasSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:objectalias-detail"
    )
    targets = SerializedPKRelatedField(
        queryset=models.ObjectAliasTarget.objects.all(),
        serializer=ObjectAliasTargetSerializer,
        required=True,
        many=True,
    )

    class Meta:
        model = models.ObjectAlias
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "targets",
        )
