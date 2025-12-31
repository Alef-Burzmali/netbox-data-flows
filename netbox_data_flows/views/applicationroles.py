from django.db.models import Count

from netbox.views import generic
from utilities.views import register_model_view

from netbox_data_flows import filtersets, forms, models, tables


__all__ = (
    "ApplicationRoleView",
    "ApplicationRoleListView",
    "ApplicationRoleEditView",
    "ApplicationRoleDeleteView",
    "ApplicationRoleBulkImportView",
    "ApplicationRoleBulkEditView",
    "ApplicationRoleBulkDeleteView",
)


@register_model_view(models.ApplicationRole, "list", path="", detail=False)
class ApplicationRoleListView(generic.ObjectListView):
    queryset = models.ApplicationRole.objects.annotate(
        application_count=Count("applications", distinct=True),
    ).order_by(*models.ApplicationRole._meta.ordering)
    table = tables.ApplicationRoleTable
    filterset = filtersets.ApplicationRoleFilterSet
    filterset_form = forms.ApplicationRoleFilterForm


@register_model_view(models.ApplicationRole)
class ApplicationRoleView(generic.ObjectView):
    queryset = models.ApplicationRole.objects.all()


@register_model_view(models.ApplicationRole, "add", detail=False)
@register_model_view(models.ApplicationRole, "edit")
class ApplicationRoleEditView(generic.ObjectEditView):
    queryset = models.ApplicationRole.objects.all()
    form = forms.ApplicationRoleForm


@register_model_view(models.ApplicationRole, "delete")
class ApplicationRoleDeleteView(generic.ObjectDeleteView):
    queryset = models.ApplicationRole.objects.all()


@register_model_view(models.ApplicationRole, "bulk_import", path="import", detail=False)
class ApplicationRoleBulkImportView(generic.BulkImportView):
    queryset = models.ApplicationRole.objects.all()
    model_form = forms.ApplicationRoleImportForm
    table = tables.ApplicationRoleTable


@register_model_view(models.ApplicationRole, "bulk_edit", path="edit", detail=False)
class ApplicationRoleBulkEditView(generic.BulkEditView):
    queryset = models.ApplicationRole.objects.annotate(
        application_count=Count("applications", distinct=True),
    ).order_by(*models.ApplicationRole._meta.ordering)
    filterset = filtersets.ApplicationRoleFilterSet
    table = tables.ApplicationRoleTable
    form = forms.ApplicationRoleBulkEditForm


@register_model_view(models.ApplicationRole, "bulk_delete", path="delete", detail=False)
class ApplicationRoleBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ApplicationRole.objects.annotate(
        application_count=Count("applications", distinct=True),
    ).order_by(*models.ApplicationRole._meta.ordering)
    filterset = filtersets.ApplicationRoleFilterSet
    table = tables.ApplicationRoleTable
