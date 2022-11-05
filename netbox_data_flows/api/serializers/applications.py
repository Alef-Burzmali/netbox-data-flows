from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from netbox_data_flows.models import Application, ApplicationRole

from .nested import NestedApplicationRoleSerializer


__all__ = (
    "ApplicationSerializer",
    "ApplicationRoleSerializer",
)


class ApplicationRoleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:applicationrole-detail"
    )
    application_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ApplicationRole
        fields = (
            "id",
            "url",
            "display",
            "name",
            "description",
            "slug",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "application_count",
        )


class ApplicationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_data_flows-api:application-detail"
    )
    dataflow_count = serializers.IntegerField(read_only=True)
    role = NestedApplicationRoleSerializer()

    class Meta:
        model = Application
        fields = (
            "id",
            "url",
            "display",
            "name",
            "role",
            "description",
            "comments",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "dataflow_count",
        )
