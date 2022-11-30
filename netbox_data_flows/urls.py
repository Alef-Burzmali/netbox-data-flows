from django.urls import path

from netbox.views.generic import ObjectChangeLogView, ObjectJournalView

from . import models, views


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
        views.ApplicationRoleView.as_view(),
        name="applicationrole",
    ),
    path(
        "application-roles/<int:pk>/edit/",
        views.ApplicationRoleEditView.as_view(),
        name="applicationrole_edit",
    ),
    path(
        "application-roles/<int:pk>/delete/",
        views.ApplicationRoleDeleteView.as_view(),
        name="applicationrole_delete",
    ),
    path(
        "application-roles/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="applicationrole_changelog",
        kwargs={"model": models.ApplicationRole},
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
        views.ApplicationView.as_view(),
        name="application",
    ),
    path(
        "applications/<int:pk>/edit/",
        views.ApplicationEditView.as_view(),
        name="application_edit",
    ),
    path(
        "applications/<int:pk>/delete/",
        views.ApplicationDeleteView.as_view(),
        name="application_delete",
    ),
    path(
        "applications/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="application_changelog",
        kwargs={"model": models.Application},
    ),
    path(
        "applications/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="application_journal",
        kwargs={"model": models.Application},
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
        views.DataFlowGroupView.as_view(),
        name="dataflowgroup",
    ),
    path(
        "dataflow-groups/<int:pk>/edit/",
        views.DataFlowGroupEditView.as_view(),
        name="dataflowgroup_edit",
    ),
    path(
        "dataflow-groups/<int:pk>/delete/",
        views.DataFlowGroupDeleteView.as_view(),
        name="dataflowgroup_delete",
    ),
    path(
        "dataflow-groups/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="dataflowgroup_changelog",
        kwargs={"model": models.DataFlowGroup},
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
        views.DataFlowView.as_view(),
        name="dataflow",
    ),
    path(
        "dataflows/<int:pk>/edit/",
        views.DataFlowEditView.as_view(),
        name="dataflow_edit",
    ),
    path(
        "dataflows/<int:pk>/delete/",
        views.DataFlowDeleteView.as_view(),
        name="dataflow_delete",
    ),
    path(
        "dataflows/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="dataflow_changelog",
        kwargs={"model": models.DataFlow},
    ),
    path(
        "dataflows/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="dataflow_journal",
        kwargs={"model": models.DataFlow},
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
        views.ObjectAliasView.as_view(),
        name="objectalias",
    ),
    path(
        "aliases/<int:pk>/link/",
        views.ObjectAliasAddTargetView.as_view(),
        name="objectalias_addtarget",
    ),
    path(
        "aliases/<int:container_pk>/unlink/<int:alias_pk>",
        views.ObjectAliasRemoveTargetView.as_view(),
        name="objectalias_removetarget",
    ),
    path(
        "aliases/<int:pk>/edit/",
        views.ObjectAliasEditView.as_view(),
        name="objectalias_edit",
    ),
    path(
        "aliases/<int:pk>/delete/",
        views.ObjectAliasDeleteView.as_view(),
        name="objectalias_delete",
    ),
    path(
        "aliases/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="objectalias_changelog",
        kwargs={"model": models.ObjectAlias},
    ),
    path(
        "aliases/<int:pk>/journal/",
        ObjectJournalView.as_view(),
        name="objectalias_journal",
        kwargs={"model": models.ObjectAlias},
    ),
)
