from django.urls import include, path

from utilities.urls import get_model_urls

from . import views


urlpatterns = tuple()

# Application Roles
urlpatterns += (
    path(
        "application-roles/",
        views.ApplicationRoleListView.as_view(),
        name="applicationrole_list",
    ),
    path(
        "application-roles/add/",
        views.ApplicationRoleEditView.as_view(),
        name="applicationrole_add",
    ),
    path(
        "application-roles/import/",
        views.ApplicationRoleBulkImportView.as_view(),
        name="applicationrole_import",
    ),
    path(
        "application-roles/edit/",
        views.ApplicationRoleBulkEditView.as_view(),
        name="applicationrole_bulk_edit",
    ),
    path(
        "application-roles/delete/",
        views.ApplicationRoleBulkDeleteView.as_view(),
        name="applicationrole_bulk_delete",
    ),
    path(
        "application-roles/<int:pk>/",
        include(get_model_urls("netbox_data_flows", "applicationrole")),
    ),
)

# Applications
urlpatterns += (
    path(
        "applications/",
        views.ApplicationListView.as_view(),
        name="application_list",
    ),
    path(
        "applications/add/",
        views.ApplicationEditView.as_view(),
        name="application_add",
    ),
    path(
        "applications/import/",
        views.ApplicationBulkImportView.as_view(),
        name="application_import",
    ),
    path(
        "applications/edit/",
        views.ApplicationBulkEditView.as_view(),
        name="application_bulk_edit",
    ),
    path(
        "applications/delete/",
        views.ApplicationBulkDeleteView.as_view(),
        name="application_bulk_delete",
    ),
    path(
        "applications/<int:pk>/",
        include(get_model_urls("netbox_data_flows", "application")),
    ),
)

# Data Flow Groups
urlpatterns += (
    path(
        "dataflow-groups/",
        views.DataFlowGroupListView.as_view(),
        name="dataflowgroup_list",
    ),
    path(
        "dataflow-groups/add/",
        views.DataFlowGroupEditView.as_view(),
        name="dataflowgroup_add",
    ),
    path(
        "dataflow-groups/import/",
        views.DataFlowGroupBulkImportView.as_view(),
        name="dataflowgroup_import",
    ),
    path(
        "dataflow-groups/edit/",
        views.DataFlowGroupBulkEditView.as_view(),
        name="dataflowgroup_bulk_edit",
    ),
    path(
        "dataflow-groups/delete/",
        views.DataFlowGroupBulkDeleteView.as_view(),
        name="dataflowgroup_bulk_delete",
    ),
    path(
        "dataflow-groups/<int:pk>/",
        include(get_model_urls("netbox_data_flows", "dataflowgroup")),
    ),
)

# Data Flows
urlpatterns += (
    path(
        "dataflows/",
        views.DataFlowListView.as_view(),
        name="dataflow_list",
    ),
    path(
        "dataflows/add/",
        views.DataFlowEditView.as_view(),
        name="dataflow_add",
    ),
    path(
        "dataflows/import/",
        views.DataFlowBulkImportView.as_view(),
        name="dataflow_import",
    ),
    path(
        "dataflows/edit/",
        views.DataFlowBulkEditView.as_view(),
        name="dataflow_bulk_edit",
    ),
    path(
        "dataflows/delete/",
        views.DataFlowBulkDeleteView.as_view(),
        name="dataflow_bulk_delete",
    ),
    path(
        "dataflows/<int:pk>/",
        include(get_model_urls("netbox_data_flows", "dataflow")),
    ),
    path(
        "dataflows/rules/",
        views.DataFlowRuleListView.as_view(),
        name="dataflow_rules",
    ),
)

# Object Aliases
urlpatterns += (
    path(
        "aliases/",
        views.ObjectAliasListView.as_view(),
        name="objectalias_list",
    ),
    path(
        "aliases/add/",
        views.ObjectAliasEditView.as_view(),
        name="objectalias_add",
    ),
    path(
        "aliases/import/",
        views.ObjectAliasBulkImportView.as_view(),
        name="objectalias_import",
    ),
    path(
        "aliases/edit/",
        views.ObjectAliasBulkEditView.as_view(),
        name="objectalias_bulk_edit",
    ),
    path(
        "aliases/delete/",
        views.ObjectAliasBulkDeleteView.as_view(),
        name="objectalias_bulk_delete",
    ),
    path(
        "aliases/<int:pk>/",
        include(get_model_urls("netbox_data_flows", "objectalias")),
    ),
)
