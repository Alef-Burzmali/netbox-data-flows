from rest_framework import serializers

from core.models import ObjectType
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


class NestableGenericObjectSerializer(GenericObjectSerializer):
    # Hack to get utilities.api.get_prefetches_for_serializer to
    # stop prefetching our fields.

    nested = True

    class Meta:
        model = ObjectType
        fields = ["object_type", "object_id"]
        brief_fields = ["object_type", "object_id"]


class ObjectAliasTargetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_data_flows-api:objectaliastarget-detail")
    target = NestableGenericObjectSerializer(
        required=True,
        many=False,
    )

    class Meta:
        model = models.ObjectAliasTarget
        fields = (
            "display",
            "id",
            "target",
            "url",
        )
        brief_fields = (
            "display",
            "id",
            "url",
        )


class ObjectAliasSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_data_flows-api:objectalias-detail")
    targets = SerializedPKRelatedField(
        queryset=models.ObjectAliasTarget.objects.all(),
        serializer=ObjectAliasTargetSerializer,
        nested=True,
        required=False,
        many=True,
    )

    class Meta:
        model = models.ObjectAlias
        fields = (
            "comments",
            "description",
            "display",
            "id",
            "name",
            "targets",
            "url",
        )
        brief_fields = (
            "description",
            "display",
            "id",
            "name",
            "url",
        )
