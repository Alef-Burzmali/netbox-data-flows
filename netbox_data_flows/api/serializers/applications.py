from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer

from tenancy.api.serializers import TenantSerializer

from netbox_data_flows import models


__all__ = (
    "ApplicationSerializer",
    "ApplicationRoleSerializer",
)


class ApplicationRoleSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_data_flows-api:applicationrole-detail")
    application_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.ApplicationRole
        fields = (
            "application_count",
            "created",
            "custom_fields",
            "description",
            "display",
            "id",
            "last_updated",
            "name",
            "slug",
            "tags",
            "url",
        )
        brief_fields = (
            "description",
            "display",
            "id",
            "name",
            "slug",
            "url",
        )


class ApplicationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_data_flows-api:application-detail")
    dataflow_count = serializers.IntegerField(read_only=True)
    role = ApplicationRoleSerializer(nested=True, required=False, allow_null=True, default=None)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, default=None)

    class Meta:
        model = models.Application
        fields = (
            "comments",
            "created",
            "custom_fields",
            "dataflow_count",
            "description",
            "display",
            "id",
            "last_updated",
            "name",
            "role",
            "tenant",
            "tags",
            "url",
        )
        brief_fields = (
            "description",
            "display",
            "id",
            "name",
            "url",
        )
