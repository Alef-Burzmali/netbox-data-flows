from django.db.models import Count
from rest_framework.routers import APIRootView

from netbox.api.viewsets import NetBoxModelViewSet

from netbox_data_flows import filtersets, models

from . import serializers


class DataFlowsRootView(APIRootView):
    def get_view_name(self):
        return "Data Flows Plugin"


class ApplicationRoleViewSet(NetBoxModelViewSet):
    queryset = models.ApplicationRole.objects.annotate(
        application_count=Count("applications"),
    )
    serializer_class = serializers.ApplicationRoleSerializer
    filterset_class = filtersets.ApplicationRoleFilterSet


class ApplicationViewSet(NetBoxModelViewSet):
    queryset = models.Application.objects.annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    serializer_class = serializers.ApplicationSerializer
    filterset_class = filtersets.ApplicationFilterSet


class DataFlowViewSet(NetBoxModelViewSet):
    queryset = models.DataFlow.objects.add_inherited_status()

    serializer_class = serializers.DataFlowSerializer
    filterset_class = filtersets.DataFlowFilterSet


class DataFlowGroupViewSet(NetBoxModelViewSet):
    queryset = models.DataFlowGroup.objects.add_related_count(
        models.DataFlowGroup.objects.all(), models.DataFlow, "group", "dataflow_count", cumulative=True
    ).add_inherited_status()

    serializer_class = serializers.DataFlowGroupSerializer
    filterset_class = filtersets.DataFlowGroupFilterSet


class ObjectAliasViewSet(NetBoxModelViewSet):
    queryset = models.ObjectAlias.objects.all()

    serializer_class = serializers.ObjectAliasSerializer
    filterset_class = filtersets.ObjectAliasFilterSet
