from django import forms

from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelImportForm
from utilities.forms.fields import CommentField, CSVModelChoiceField, DynamicModelChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet

from tenancy.forms import ContactModelFilterForm, TenancyFilterForm, TenancyForm
from tenancy.models import Tenant

from netbox_data_flows.models import Application, ApplicationRole


__all__ = (
    "ApplicationForm",
    "ApplicationBulkEditForm",
    "ApplicationImportForm",
    "ApplicationFilterForm",
)

#
# Object forms
#


class ApplicationForm(TenancyForm, NetBoxModelForm):
    role = DynamicModelChoiceField(
        queryset=ApplicationRole.objects.all(),
        required=False,
        quick_add=True,
    )
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "name",
            "role",
            "description",
            "tags",
        ),
        FieldSet(
            "tenant_group",
            "tenant",
            name="Tenancy",
        ),
    )

    class Meta:
        model = Application
        fields = (
            "name",
            "role",
            "description",
            "tenant",
            "comments",
            "tags",
        )


#
# Bulk forms
#


class ApplicationBulkEditForm(NetBoxModelBulkEditForm):
    model = Application

    description = forms.CharField(max_length=200, required=False)
    role = DynamicModelChoiceField(
        queryset=ApplicationRole.objects.all(),
        required=False,
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "role",
            "tenant",
            "description",
        ),
    )
    nullable_fields = (
        "role",
        "tenant",
        "description",
        "comments",
    )


class ApplicationImportForm(NetBoxModelImportForm):
    role = CSVModelChoiceField(
        queryset=ApplicationRole.objects.all(),
        required=False,
        to_field_name="slug",
        help_text="Role of the application",
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned tenant",
    )

    class Meta:
        model = Application
        fields = (
            "name",
            "description",
            "comments",
            "role",
            "tenant",
        )


#
# Filter forms
#


class ApplicationFilterForm(ContactModelFilterForm, TenancyFilterForm, NetBoxModelFilterSetForm):
    model = Application
    tag = TagFilterField(model)

    role = forms.ModelMultipleChoiceField(queryset=ApplicationRole.objects.all(), required=False)

    selector_fields = (
        "filter_id",
        "q",
        "role",
    )
    fieldsets = (
        FieldSet(
            "filter_id",  # Saved Filter
            "q",  # Search
            "tag",
        ),
        FieldSet(
            "role",
            name="Application Role",
        ),
        FieldSet(
            "tenant_group_id",
            "tenant_id",
            name="Tenancy",
        ),
        FieldSet(
            "contact",
            "contact_role",
            "contact_group",
            name="Contacts",
        ),
    )
