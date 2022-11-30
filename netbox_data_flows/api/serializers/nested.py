from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer

from netbox_data_flows import models


__all__ = (
    "NestedApplicationSerializer",
    "NestedApplicationRoleSerializer",
    "NestedDataFlowSerializer",
    "NestedDataFlowGroupSerializer",
    "NestedObjectAliasSerializer",
    "NestedObjectAliasTargetSerializer",
)


#
# applications
#


class NestedApplicationRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:applicationrole-detail"
    )

    class Meta:
        model = models.ApplicationRole
        fields = ("id", "url", "display", "slug")


class NestedApplicationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:application-detail"
    )
    role = NestedApplicationRoleSerializer()

    class Meta:
        model = models.Application
        fields = ("id", "url", "display", "role")


#
# dataflows
#


class NestedDataFlowSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:dataflow-detail"
    )
    _depth = serializers.IntegerField(source="level", read_only=True)
    application = NestedApplicationSerializer()

    class Meta:
        model = models.DataFlow
        fields = (
            "id",
            "url",
            "display",
            "application",
            "name",
            "status",
            "_depth",
        )


#
# dataflow groups
#


class NestedDataFlowGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:dataflowgroup-detail"
    )
    _depth = serializers.IntegerField(source="level", read_only=True)
    application = NestedApplicationSerializer()

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "id",
            "url",
            "display",
            "application",
            "name",
            "status",
            "_depth",
        )


#
# Object aliases
#


class NestedObjectAliasTargetSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:objectaliastarget-detail"
    )

    class Meta:
        model = models.ObjectAliasTarget
        fields = (
            "id",
            "url",
            "display",
        )


class NestedObjectAliasSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:objectalias-detail"
    )

    class Meta:
        model = models.ObjectAlias
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
        )
