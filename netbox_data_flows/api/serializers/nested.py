from rest_framework import serializers

from netbox.api.serializers import WritableNestedSerializer

from netbox_data_flows.models import (
    Application,
    ApplicationRole,
    DataFlow,
    DataFlowTemplate,
)


__all__ = (
    "NestedApplicationSerializer",
    "NestedApplicationRoleSerializer",
    "NestedDataFlowSerializer",
    "NestedDataFlowTemplateSerializer",
)


#
# applications
#


class NestedApplicationRoleSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:applicationrole-detail"
    )

    class Meta:
        model = ApplicationRole
        fields = ("id", "url", "display", "slug")


class NestedApplicationSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:application-detail"
    )
    role = NestedApplicationRoleSerializer()

    class Meta:
        model = Application
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
        model = DataFlow
        fields = (
            "id",
            "url",
            "display",
            "application",
            "name",
            "status",
            "_depth",
        )


class NestedDataFlowTemplateSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:dataflowtemplate-detail"
    )
    _depth = serializers.IntegerField(source="level", read_only=True)

    class Meta:
        model = DataFlowTemplate
        fields = ("id", "url", "display", "name", "status", "_depth")
