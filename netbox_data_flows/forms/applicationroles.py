from netbox.forms import (
    OrganizationalModelBulkEditForm,
    OrganizationalModelFilterSetForm,
    OrganizationalModelForm,
    OrganizationalModelImportForm,
)
from utilities.forms.fields import TagFilterField
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


class ApplicationRoleForm(OrganizationalModelForm):
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
        fields = (
            "comments",
            "description",
            "name",
            "owner",
            "slug",
            "tags",
        )


#
# Bulk forms
#


class ApplicationRoleBulkEditForm(OrganizationalModelBulkEditForm):
    model = ApplicationRole

    fieldsets = (
        FieldSet(
            "description",
        ),
    )
    nullable_fields = (
        "comments",
        "description",
        "owner",
    )


class ApplicationRoleImportForm(OrganizationalModelImportForm):
    class Meta:
        model = ApplicationRole
        fields = (
            "name",
            "slug",
            "description",
            "owner",
            "comments",
            "tags",
        )


#
# Filter forms
#


class ApplicationRoleFilterForm(OrganizationalModelFilterSetForm):
    model = ApplicationRole
    tag = TagFilterField(model)

    fieldsets = (
        FieldSet(
            "filter_id",  # Saved Filter
            "q",  # Search
            "tag",
            "owner_id",
        ),
    )
