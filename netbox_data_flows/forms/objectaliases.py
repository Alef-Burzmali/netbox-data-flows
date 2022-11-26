from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelCSVForm,
    NetBoxModelFilterSetForm,
)
from utilities.forms import (
    TagFilterField,
)

from netbox_data_flows.models import (
    ObjectAlias,
)

__all__ = (
    "ObjectAliasForm",
    "ObjectAliasBulkEditForm",
    "ObjectAliasCSVForm",
)

#
# Object forms
#


class ObjectAliasForm(NetBoxModelForm):
    fieldsets = (
        (
            None,
            (
                "name",
                "description",
                "tags",
            ),
        ),
    )

    class Meta:
        model = ObjectAlias
        fields = ("name", "description", "tags")


#
# Bulk forms
#


class ObjectAliasBulkEditForm(NetBoxModelBulkEditForm):
    model = ObjectAlias

    description = forms.CharField(max_length=200, required=False)

    fieldsets = (
        (
            None,
            ("description",),
        ),
    )
    nullable_fields = ("description",)


class ObjectAliasCSVForm(NetBoxModelCSVForm):
    class Meta:
        model = ObjectAlias
        fields = (
            "name",
            "description",
        )


#
# Filter forms
#


class ObjectAliasFilterForm(NetBoxModelFilterSetForm):
    model = ObjectAlias
    tag = TagFilterField(model)
