from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
)
from utilities.forms.fields import (
    TagFilterField,
    DynamicModelMultipleChoiceField,
)

from dcim.models import Device
from ipam.models import Prefix, IPRange, IPAddress
from virtualization.models import VirtualMachine

from netbox_data_flows import models
from netbox_data_flows.utils.aliases import AddAliasesForm

__all__ = (
    "ObjectAliasForm",
    "ObjectAliasBulkEditForm",
    "ObjectAliasFilterForm",
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
        fields = (
            "name",
            "description",
            "tags",
        )


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

    prefixes = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Aliased Prefixes",
    )
    ipranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="Aliased IP Ranges",
    )
    ipaddresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Aliased IP Addresses",
    )
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Aliased Devices",
        help_text="Any IP addresses of the device",
    )
    virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Aliased Virtual Machines",
        help_text="Any IP address of the virtual machine",
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
            "Targets - all targets are OR'ed together, any will match",
            (
                "prefixes",
                "ipranges",
                "ipaddresses",
                "devices",
                "virtual_machines",
            ),
        ),
    )


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
        queryset=Prefix.objects.all(),
        required=False,
        selector=True,
        label="Aliased Prefixes",
    )
    aliased_ipranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        selector=True,
        label="Aliased IP Ranges",
    )
    aliased_ipaddresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        selector=True,
        label="Aliased IP Addresses",
    )
