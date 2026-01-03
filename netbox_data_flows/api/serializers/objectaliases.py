from rest_framework import serializers

from netbox.api.fields import SerializedPKRelatedField
from netbox.api.serializers import PrimaryModelSerializer

from ipam.api.serializers import IPAddressSerializer, IPRangeSerializer, PrefixSerializer
from ipam.models import IPAddress, IPRange, Prefix

from netbox_data_flows import models


__all__ = ("ObjectAliasSerializer",)


class ObjectAliasSerializer(PrimaryModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_data_flows-api:objectalias-detail")
    prefixes = SerializedPKRelatedField(
        queryset=Prefix.objects.all(),
        serializer=PrefixSerializer,
        nested=True,
        required=False,
        many=True,
    )
    ip_ranges = SerializedPKRelatedField(
        queryset=IPRange.objects.all(),
        serializer=IPRangeSerializer,
        nested=True,
        required=False,
        many=True,
    )
    ip_addresses = SerializedPKRelatedField(
        queryset=IPAddress.objects.all(),
        serializer=IPAddressSerializer,
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
            "prefixes",
            "ip_ranges",
            "ip_addresses",
            "tags",
            "owner",
            "url",
        )
        brief_fields = (
            "description",
            "display",
            "id",
            "name",
            "url",
        )
