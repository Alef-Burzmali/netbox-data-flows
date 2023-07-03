from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
)
from tenancy.forms import ContactModelFilterForm
from utilities.forms.fields import (
    CommentField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    TagFilterField,
)

from netbox_data_flows.models import (
    Application,
    ApplicationRole,
)


__all__ = (
    "ApplicationForm",
    "ApplicationBulkEditForm",
    "ApplicationImportForm",
    "ApplicationFilterForm",
)

#
# Object forms
#


class ApplicationForm(NetBoxModelForm):
    role = DynamicModelChoiceField(
        queryset=ApplicationRole.objects.all(),
        required=False,
        selector=True,
    )
    comments = CommentField()

    fieldsets = (
        (
            "Application",
            (
                "name",
                "role",
                "description",
                "tags",
            ),
        ),
    )

    class Meta:
        model = Application
        fields = (
            "name",
            "role",
            "description",
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
        selector=True,
    )
    comments = CommentField()

    fieldsets = (
        (
            "Application",
            (
                "role",
                "description",
            ),
        ),
    )
    nullable_fields = (
        "role",
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

    class Meta:
        model = Application
        fields = (
            "name",
            "description",
            "role",
        )


#
# Filter forms
#


class ApplicationFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Application
    tag = TagFilterField(model)

    role = forms.ModelMultipleChoiceField(
        queryset=ApplicationRole.objects.all(), required=False
    )

    fieldsets = (
        (
            None,
            (
                "filter_id",  # Saved Filter
                "q",  # Search
                "tag",
            ),
        ),
        (
            "Application Role",
            ("role",),
        ),
        (
            "Contacts",
            (
                "contact",
                "contact_role",
                "contact_group",
            ),
        ),
    )
