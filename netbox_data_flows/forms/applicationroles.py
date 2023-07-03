from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
)
from utilities.forms.fields import (
    SlugField,
    TagFilterField,
)

from netbox_data_flows.models import (
    ApplicationRole,
)

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

    fieldsets = (
        (
            "Application Role",
            (
                "name",
                "slug",
                "description",
                "tags",
            ),
        ),
    )

    class Meta:
        model = ApplicationRole
        fields = ("name", "slug", "description", "tags")


#
# Bulk forms
#


class ApplicationRoleBulkEditForm(NetBoxModelBulkEditForm):
    model = ApplicationRole

    description = forms.CharField(max_length=200, required=False)

    fieldsets = (
        (
            "Application Role",
            ("description",),
        ),
    )
    nullable_fields = ("description",)


class ApplicationRoleImportForm(NetBoxModelImportForm):
    class Meta:
        model = ApplicationRole
        fields = (
            "name",
            "slug",
            "description",
        )


#
# Filter forms
#


class ApplicationRoleFilterForm(NetBoxModelFilterSetForm):
    model = ApplicationRole
    tag = TagFilterField(model)
