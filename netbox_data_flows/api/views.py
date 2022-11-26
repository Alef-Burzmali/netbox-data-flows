from django.db.models import Count
from rest_framework.routers import APIRootView
from rest_framework.viewsets import ModelViewSet

from netbox.api.viewsets import NetBoxModelViewSet

from netbox_data_flows import filtersets, models

from . import serializers


class DataFlowsRootView(APIRootView):
    def get_view_name(self):
        return "Data Flows Plugin"


class ApplicationRoleViewSet(NetBoxModelViewSet):
    queryset = models.ApplicationRole.objects.prefetch_related(
        "tags"
    ).annotate(
        application_count=Count("applications"),
    )
    serializer_class = serializers.ApplicationRoleSerializer
    filterset_class = filtersets.ApplicationRoleFilterSet


class ApplicationViewSet(NetBoxModelViewSet):
    queryset = models.Application.objects.prefetch_related(
        "role",
        "tags",
    ).annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    serializer_class = serializers.ApplicationSerializer
    filterset_class = filtersets.ApplicationFilterSet


class DataFlowViewSet(NetBoxModelViewSet):
    queryset = models.DataFlow.objects.prefetch_related(
        "application",
        "source_device",
        "source_virtual_machine",
        "source_prefix",
        "source_ipaddress",
        "destination_device",
        "destination_virtual_machine",
        "destination_prefix",
        "destination_ipaddress",
        "tags",
    )

    serializer_class = serializers.DataFlowSerializer
    filterset_class = filtersets.DataFlowFilterSet


class DataFlowTemplateViewSet(NetBoxModelViewSet):
    queryset = models.DataFlowTemplate.objects.prefetch_related(
        "source_device",
        "source_virtual_machine",
        "source_prefix",
        "source_ipaddress",
        "destination_device",
        "destination_virtual_machine",
        "destination_prefix",
        "destination_ipaddress",
        "tags",
    )

    serializer_class = serializers.DataFlowTemplateSerializer
    filterset_class = filtersets.DataFlowTemplateFilterSet


class ObjectAliasTargetViewSet(NetBoxModelViewSet):
    queryset = models.ObjectAliasTarget.objects.prefetch_related(
        "aliased_object",
    )

    serializer_class = serializers.ObjectAliasTargetSerializer
    # filterset_class = filtersets.DataFlowFilterSet


class ObjectAliasViewSet(NetBoxModelViewSet):
    queryset = models.ObjectAlias.objects.prefetch_related(
        "targets",
        "tags",
    )

    serializer_class = serializers.ObjectAliasSerializer
    filterset_class = filtersets.ObjectAliasFilterSet
