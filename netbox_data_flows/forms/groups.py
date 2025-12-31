from django import forms

from netbox.forms import (
    NestedGroupModelBulkEditForm,
    NestedGroupModelFilterSetForm,
    NestedGroupModelForm,
    NestedGroupModelImportForm,
)
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from tenancy.forms import TenancyFilterForm, TenancyForm
from tenancy.models import Tenant

from netbox_data_flows import choices, models


__all__ = (
    "DataFlowGroupForm",
    "DataFlowGroupBulkEditForm",
    "DataFlowGroupFilterForm",
    "DataFlowGroupImportForm",
)

#
# Object forms
#


class DataFlowGroupForm(TenancyForm, NestedGroupModelForm):
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
        selector=True,
        help_text="Application that this data flow group is related to.",
    )
    parent = DynamicModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        selector=True,
        help_text="Parent group of this Data Flow Group.",
    )

    fieldsets = (
        FieldSet(
            "application",
            "parent",
            "name",
            "slug",
            "description",
            "status",
            "tags",
        ),
        FieldSet(
            "tenant_group",
            "tenant",
            name="Tenancy",
        ),
    )

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "application",
            "comments",
            "description",
            "name",
            "owner",
            "parent",
            "slug",
            "status",
            "tags",
            "tenant",
        )
        help_texts = {
            "status": (
                "Status of the data flow group. Disabling a parent disables "
                "all its descendants and their data flows."
            )
        }


#
# Bulk forms
#


class DataFlowGroupBulkEditForm(NestedGroupModelBulkEditForm):
    model = models.DataFlowGroup

    description = forms.CharField(max_length=200, required=False)
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
    )
    parent = DynamicModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )

    fieldsets = (
        FieldSet(
            "application",
            "parent",
            "tenant",
            "description",
            "status",
        ),
    )
    nullable_fields = (
        "application",
        "comments",
        "owner",
        "parent",
        "tenant",
    )


class DataFlowGroupImportForm(NestedGroupModelImportForm):
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Application",
    )
    parent = CSVModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        to_field_name="slug",
        help_text="Parent group of the data flow group",
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned tenant",
    )
    status = CSVChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
        help_text="Status",
    )

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "name",
            "slug",
            "description",
            "application",
            "parent",
            "tenant",
            "status",
            "owner",
            "comments",
            "tags",
        )


#
# Filter forms
#


class DataFlowGroupFilterForm(TenancyFilterForm, NestedGroupModelFilterSetForm):
    model = models.DataFlowGroup

    tag = TagFilterField(model)

    application = DynamicModelMultipleChoiceField(queryset=models.Application.objects.all(), required=False)
    application_role = DynamicModelMultipleChoiceField(queryset=models.ApplicationRole.objects.all(), required=False)
    parent_id = DynamicModelMultipleChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        label="Parent group",
        help_text="Direct parent group(s)",
    )
    ancestor_id = DynamicModelMultipleChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        label="Ancestor group",
        help_text="Recursive parent group(s)",
    )

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )
    inherited_status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )

    selector_fields = ("filter_id", "q", "application", "ancestor_id")
    fieldsets = (
        FieldSet(
            "filter_id",  # Saved Filter
            "q",  # Search
            "tag",
            "owner_id",
        ),
        FieldSet(
            "application",
            "application_role",
            "parent_id",
            "ancestor_id",
        ),
        FieldSet(
            "tenant_group_id",
            "tenant_id",
            name="Tenancy",
        ),
        FieldSet(
            "status",
            "inherited_status",
            name="Status",
        ),
    )
