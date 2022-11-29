from rest_framework import serializers

from netbox.api.fields import ChoiceField, SerializedPKRelatedField
from netbox.api.serializers import NetBoxModelSerializer

from dcim.api.serializers import NestedDeviceSerializer
from ipam.models import IPAddress
from ipam.api.serializers import (
    NestedPrefixSerializer,
    NestedIPAddressSerializer,
)
from virtualization.api.serializers import NestedVirtualMachineSerializer

from netbox_data_flows.models import DataFlow
from netbox_data_flows.choices import (
    DataFlowProtocolChoices,
    DataFlowStatusChoices,
    DataFlowInheritedStatusChoices,
)

from .nested import (
    NestedApplicationSerializer,
    NestedDataFlowSerializer,
)


__all__ = ("DataFlowSerializer",)


class DataFlowSerializerBase(serializers.Serializer):
    status = ChoiceField(choices=DataFlowStatusChoices, required=False)
    inherited_status = ChoiceField(
        choices=DataFlowInheritedStatusChoices, required=False, read_only=True
    )
    protocol = ChoiceField(choices=DataFlowProtocolChoices, required=False)

    source_device = NestedDeviceSerializer(
        required=False, allow_null=True, default=None
    )
    source_virtual_machine = NestedVirtualMachineSerializer(
        required=False, allow_null=True, default=None
    )
    source_prefix = NestedPrefixSerializer(
        required=False, allow_null=True, default=None
    )
    source_ipaddress = NestedIPAddressSerializer(
        required=False, allow_null=True, default=None
    )

    destination_device = NestedDeviceSerializer(
        required=False, allow_null=True, default=None
    )
    destination_virtual_machine = NestedVirtualMachineSerializer(
        required=False, allow_null=True, default=None
    )
    destination_prefix = NestedPrefixSerializer(
        required=False, allow_null=True, default=None
    )
    destination_ipaddress = NestedIPAddressSerializer(
        required=False, allow_null=True, default=None
    )

    class Meta:
        abstract = True


class DataFlowSerializer(NetBoxModelSerializer, DataFlowSerializerBase):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:dataflow-detail"
    )
    application = NestedApplicationSerializer(required=True)
    parent = NestedDataFlowSerializer(
        required=False, allow_null=True, default=None
    )
    _depth = serializers.IntegerField(source="level", read_only=True)

    class Meta:
        model = DataFlow
        fields = (
            "id",
            "url",
            "display",
            "application",
            "name",
            "status",
            "inherited_status",
            "parent",
            "_depth",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "protocol",
            "source_ports",
            "destination_ports",
            "source_device",
            "source_virtual_machine",
            "source_prefix",
            "source_ipaddress",
            "destination_device",
            "destination_virtual_machine",
            "destination_prefix",
            "destination_ipaddress",
        )
