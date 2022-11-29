from rest_framework import serializers

from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import (
    NetBoxModelSerializer,
    GenericObjectSerializer,
)

from netbox_data_flows import models, choices

from .nested import *


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
            "type",
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
            "name",
            "description",
            "size",
            "type",
            "targets",
        )
