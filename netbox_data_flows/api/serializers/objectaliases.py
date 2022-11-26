from rest_framework import serializers

from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import (
    NetBoxModelSerializer,
    GenericObjectSerializer,
)

from netbox_data_flows.models import ObjectAlias, ObjectAliasTarget

# from .nested import (
#    NestedObjectAliasTargetSerializer,
# )


__all__ = (
    "ObjectAliasTargetSerializer",
    "ObjectAliasSerializer",
)


class ObjectAliasTargetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:objectaliastarget-detail"
    )
    aliased_object = GenericObjectSerializer(
        required=True,
        many=False,
    )

    class Meta:
        model = ObjectAliasTarget
        fields = (
            "id",
            "url",
            "type",
            "aliased_object",
        )


class ObjectAliasSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:objectalias-detail"
    )
    targets = ObjectAliasTargetSerializer(required=True, many=True)

    class Meta:
        model = ObjectAlias
        fields = (
            "id",
            "url",
            "name",
            "description",
            "size",
            "type",
            "targets",
        )
