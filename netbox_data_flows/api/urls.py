from netbox.api.routers import NetBoxRouter

from . import views


app_name = "netbox_data_flows"

router = NetBoxRouter()
router.APIRootView = views.DataFlowsRootView

router.register("application-roles", views.ApplicationRoleViewSet)
router.register("applications", views.ApplicationViewSet)
router.register("dataflows", views.DataFlowViewSet)
router.register("dataflow-templates", views.DataFlowTemplateViewSet)
router.register("objectalias-target", views.ObjectAliasTargetViewSet)
router.register("objectalias", views.ObjectAliasViewSet)

urlpatterns = router.urls
