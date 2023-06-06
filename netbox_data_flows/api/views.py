from django.db.models import Count
from rest_framework.routers import APIRootView

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
        "group",
        "sources",
        "destinations",
        "tags",
    )

    serializer_class = serializers.DataFlowSerializer
    filterset_class = filtersets.DataFlowFilterSet


class DataFlowGroupViewSet(NetBoxModelViewSet):
    queryset = models.DataFlowGroup.objects.prefetch_related(
        "application",
        "parent",
        "tags",
    )

    serializer_class = serializers.DataFlowGroupSerializer
    filterset_class = filtersets.DataFlowGroupFilterSet


class ObjectAliasTargetViewSet(NetBoxModelViewSet):
    queryset = models.ObjectAliasTarget.objects.prefetch_related(
        "target",
    )

    serializer_class = serializers.ObjectAliasTargetSerializer
    filterset_class = filtersets.ObjectAliasTargetFilterSet


class ObjectAliasViewSet(NetBoxModelViewSet):
    queryset = models.ObjectAlias.objects.prefetch_related(
        "targets",
        "tags",
    )

    serializer_class = serializers.ObjectAliasSerializer
    filterset_class = filtersets.ObjectAliasFilterSet
