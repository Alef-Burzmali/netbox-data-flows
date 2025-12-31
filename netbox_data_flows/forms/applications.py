from django import forms

from netbox.forms import PrimaryModelBulkEditForm, PrimaryModelFilterSetForm, PrimaryModelForm, PrimaryModelImportForm
from utilities.forms.fields import CSVModelChoiceField, DynamicModelChoiceField, TagFilterField
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


class ApplicationForm(TenancyForm, PrimaryModelForm):
    role = DynamicModelChoiceField(
        queryset=ApplicationRole.objects.all(),
        required=False,
        quick_add=True,
    )

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
            "comments",
            "description",
            "name",
            "owner",
            "role",
            "tags",
            "tenant",
            "tenant_group",
        )


#
# Bulk forms
#


class ApplicationBulkEditForm(PrimaryModelBulkEditForm):
    model = Application

    role = DynamicModelChoiceField(
        queryset=ApplicationRole.objects.all(),
        required=False,
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
    )

    fieldsets = (
        FieldSet(
            "role",
            "description",
            "tenant",
        ),
    )
    nullable_fields = (
        "comments",
        "description",
        "owner",
        "role",
        "tenant",
    )


class ApplicationImportForm(PrimaryModelImportForm):
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
            "role",
            "tenant",
            "owner",
            "comments",
            "tags",
        )


#
# Filter forms
#


class ApplicationFilterForm(ContactModelFilterForm, TenancyFilterForm, PrimaryModelFilterSetForm):
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
            "owner_id",
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
