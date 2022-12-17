from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
)
from utilities.forms import (
    TagFilterField,
    DynamicModelMultipleChoiceField,
)

from ipam.models import Prefix, IPRange, IPAddress

from netbox_data_flows import models
from netbox_data_flows.utils.aliases import AddAliasesForm

__all__ = (
    "ObjectAliasForm",
    "ObjectAliasBulkEditForm",
    "ObjectAliasImportForm",
    "ObjectAliasAddTargetForm",
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
        model = models.ObjectAlias
        fields = ("name", "description", "tags")


#
# Bulk forms
#


class ObjectAliasBulkEditForm(NetBoxModelBulkEditForm):
    model = models.ObjectAlias

    description = forms.CharField(max_length=200, required=False)

    fieldsets = (
        (
            None,
            ("description",),
        ),
    )
    nullable_fields = ("description",)


class ObjectAliasImportForm(NetBoxModelImportForm):
    class Meta:
        model = models.ObjectAlias
        fields = (
            "name",
            "description",
        )


#
# Filter forms
#


class ObjectAliasFilterForm(NetBoxModelFilterSetForm):
    model = models.ObjectAlias
    tag = TagFilterField(model)


#
# Special forms
#


class ObjectAliasAddTargetForm(AddAliasesForm):
    model = models.ObjectAlias
    aliased_fields = (
        "aliased_prefixes",
        "aliased_ipranges",
        "aliased_ipaddresses",
    )

    aliased_prefixes = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(), required=False, label="Aliased Prefixes"
    )
    aliased_ipranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="Aliased IP Ranges",
    )
    aliased_ipaddresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Aliased IP Addresses",
    )
