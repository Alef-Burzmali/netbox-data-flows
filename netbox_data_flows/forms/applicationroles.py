from django import forms

from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelImportForm
from utilities.forms.fields import CommentField, SlugField, TagFilterField
from utilities.forms.rendering import FieldSet

from netbox_data_flows.models import ApplicationRole


__all__ = (
    "ApplicationRoleForm",
    "ApplicationRoleBulkEditForm",
    "ApplicationRoleImportForm",
    "ApplicationRoleFilterForm",
)

#
# Object forms
#


class ApplicationRoleForm(NetBoxModelForm):
    slug = SlugField()
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "name",
            "slug",
            "description",
            "tags",
        ),
    )

    class Meta:
        model = ApplicationRole
        fields = ("name", "slug", "description", "comments", "tags")


#
# Bulk forms
#


class ApplicationRoleBulkEditForm(NetBoxModelBulkEditForm):
    model = ApplicationRole

    description = forms.CharField(max_length=200, required=False)
    comments = CommentField()

    fieldsets = (
        FieldSet(
            "description",
        ),
    )
    nullable_fields = (
        "description",
        "comments",
    )


class ApplicationRoleImportForm(NetBoxModelImportForm):
    class Meta:
        model = ApplicationRole
        fields = (
            "name",
            "slug",
            "description",
            "comments",
        )


#
# Filter forms
#


class ApplicationRoleFilterForm(NetBoxModelFilterSetForm):
    model = ApplicationRole
    tag = TagFilterField(model)
