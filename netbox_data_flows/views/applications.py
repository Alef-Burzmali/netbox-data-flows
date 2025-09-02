from django.db.models import Count

from netbox.views import generic
from utilities.views import register_model_view


try:
    from netbox.views.generic import ObjectContactsView
except ImportError:
    # FIXME: Compat NetBox <=4.2
    from tenancy.views import ObjectContactsView

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
    queryset = (
        models.Application.objects.prefetch_related("role")
        .annotate(
            dataflow_count=Count("dataflows", distinct=True),
        )
        .order_by(*models.Application._meta.ordering)
    )
    table = tables.ApplicationTable
    filterset = filtersets.ApplicationFilterSet
    filterset_form = forms.ApplicationFilterForm


@register_model_view(models.Application)
class ApplicationView(GetRelatedCustomFieldModelsMixin, generic.ObjectView):
    queryset = models.Application.objects.prefetch_related("role", "contacts", "dataflows", "dataflow_groups")
    custom_field_setting = "application_custom_field"

    def get_extra_context(self, request, instance):
        related_models = self.get_related_models(request, instance)

        dataflowgroups_table = tables.DataFlowGroupTable(
            instance.dataflow_groups.prefetch_related(
                "application",
                "application__role",
                "parent",
            ).annotate(
                dataflow_count=Count("dataflows", distinct=True),
            )
        )
        dataflowgroups_table.configure(request)

        dataflows_table = tables.DataFlowTable(
            instance.dataflows.prefetch_related(
                "application",
                "application__role",
                "group",
                "sources",
                "destinations",
            )
        )
        dataflows_table.configure(request)

        return {
            "related_models": related_models,
            "dataflowgroups_table": dataflowgroups_table,
            "dataflows_table": dataflows_table,
        }


@register_model_view(models.Application, "add", detail=False)
@register_model_view(models.Application, "edit")
class ApplicationEditView(generic.ObjectEditView):
    queryset = models.Application.objects.prefetch_related("role")
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
    queryset = models.Application.objects.prefetch_related("role").annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable
    form = forms.ApplicationBulkEditForm


@register_model_view(models.Application, "bulk_delete", path="delete", detail=False)
class ApplicationBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Application.objects.prefetch_related("role").annotate(
        dataflow_count=Count("dataflows", distinct=True),
    )
    filterset = filtersets.ApplicationFilterSet
    table = tables.ApplicationTable


@register_model_view(models.Application, "contacts")
class ApplicationContactsView(ObjectContactsView):
    queryset = models.Application.objects.all()
