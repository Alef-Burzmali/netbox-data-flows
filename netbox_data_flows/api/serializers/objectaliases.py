from rest_framework import serializers

from extras.models import Tag
from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NestedTagSerializer, PrimaryModelSerializer

from ipam.api.serializers import IPAddressSerializer, IPRangeSerializer, PrefixSerializer
from ipam.models import IPAddress, IPRange, Prefix

from netbox_data_flows import choices, models

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
    device_tags = SerializedPKRelatedField(
        queryset=Tag.objects.all(),
        serializer=NestedTagSerializer,
        nested=True,
        required=False,
        many=True,
    )
    virtual_machine_tags = SerializedPKRelatedField(
        queryset=Tag.objects.all(),
        serializer=NestedTagSerializer,
        nested=True,
        required=False,
        many=True,
    )
    tag_matching_rule = ChoiceField(
        choices=choices.TagMatchingRuleChoices,
        required=False,
        default=choices.TagMatchingRuleChoices.MATCHING_PRIMARY,
    )

    class Meta:
        model = models.ObjectAlias
        fields = (
            "comments",
            "description",
            "device_tags",
            "display",
            "id",
            "ip_addresses",
            "ip_ranges",
            "name",
            "owner",
            "prefixes",
            "tag_matching_rule",
            "tags",
            "url",
            "virtual_machine_tags",
        )
        brief_fields = (
            "description",
            "display",
            "id",
            "name",
            "url",
        )
