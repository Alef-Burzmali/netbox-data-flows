from django.db.models import Count

from netbox.views import generic
from utilities.views import register_model_view

from netbox_data_flows import filtersets, forms, models, tables
from netbox_data_flows.utils.views import GetRelatedCustomFieldModelsMixin


__all__ = (
    "ApplicationView",
    "ApplicationListView",
    "ApplicationEditView",
    "ApplicationDeleteView",
    "ApplicationBulkImportView",
    "ApplicationBulkEditView",
    "ApplicationBulkDeleteView",
)


@register_model_view(models.Application, "list", path="", detail=False)
class ApplicationListView(generic.ObjectListView):
    queryset = models.Application.objects.annotate(
        dataflow_count=Count("dataflows", distinct=True),
    ).order_by(*models.Application._meta.ordering)
    table = tables.ApplicationTable
    filterset = filtersets.ApplicationFilterSet
    filterset_form = forms.ApplicationFilterForm


@register_model_view(models.Application)
class ApplicationView(GetRelatedCustomFieldModelsMixin, generic.ObjectView):
    queryset = models.Application.objects.all()
    custom_field_setting = "application_custom_field"

    def get_extra_context(self, request, instance):
        related_models = self.get_related_models(request, instance)

        return {
            "related_models": related_models,
        }


@register_model_view(models.Application, "add", detail=False)
@register_model_view(models.Application, "edit")
class ApplicationEditView(generic.ObjectEditView):
    queryset = models.Application.objects.all()
    form = forms.ApplicationForm


@register_model_view(models.Application, "delete")
class ApplicationDeleteView(generic.ObjectDeleteView):
    queryset = models.Application.objects.all()


@register_model_view(models.Application, "bulk_import", path="import", detail=False)
class ApplicationBulkImportView(generic.BulkImportView):
    queryset = models.Application.objects.all()
    model_form = forms.ApplicationImportForm
    table = tables.ApplicationTable


@register_model_view(models.Application, "bulk_edit", path="edit", detail=False)
class ApplicationBulkEditView(generic.BulkEditView):
    queryset = models.Application.objects.annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable
    form = forms.ApplicationBulkEditForm


@register_model_view(models.Application, "bulk_delete", path="delete", detail=False)
class ApplicationBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Application.objects.annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable
