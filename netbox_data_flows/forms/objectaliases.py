from django import forms

from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelImportForm
from utilities.forms.fields import CommentField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine

from netbox_data_flows import models


__all__ = (
    "ObjectAliasForm",
    "ObjectAliasBulkEditForm",
    "ObjectAliasFilterForm",
    "ObjectAliasImportForm",
)

#
# Object forms
#


class ObjectAliasForm(NetBoxModelForm):
    comments = CommentField()

    prefixes = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        selector=True,
        label="Prefixes",
    )
    ip_ranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        selector=True,
        label="IP Ranges",
    )
    ip_addresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        selector=True,
        label="IP Addresses",
    )

    fieldsets = (
        FieldSet(
            "name",
            "description",
            "tags",
        ),
        FieldSet("prefixes", "ip_ranges", "ip_addresses", name="Aliased objects"),
    )

    class Meta:
        model = models.ObjectAlias
        fields = (
            "name",
            "description",
            "tags",
            "comments",
            "prefixes",
            "ip_ranges",
            "ip_addresses",
        )


#
# Bulk forms
#


class ObjectAliasBulkEditForm(NetBoxModelBulkEditForm):
    model = models.ObjectAlias
    comments = CommentField()

    description = forms.CharField(max_length=200, required=False)

    prefixes = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        selector=True,
        label="Prefixes",
    )
    ip_ranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        selector=True,
        label="IP Ranges",
    )
    ip_addresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        selector=True,
        label="IP Addresses",
    )

    fieldsets = (
        FieldSet(
            "description",
            "comments",
        ),
        FieldSet("prefixes", "ip_ranges", "ip_addresses", name="Aliased objects"),
    )
    nullable_fields = (
        "description",
        "comments",
        "prefixes",
        "ip_ranges",
        "ip_addresses",
    )


class ObjectAliasImportForm(NetBoxModelImportForm):
    class Meta:
        model = models.ObjectAlias
        fields = (
            "name",
            "description",
            "comments",
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
        label="Prefixes",
    )
    ip_ranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="IP Ranges",
    )
    ip_addresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="IP Addresses",
    )
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Devices",
        help_text="Any IP addresses of the device",
    )
    virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Virtual Machines",
        help_text="Any IP address of the virtual machine",
    )

    fieldsets = (
        FieldSet(
            "filter_id",  # Saved Filter
            "q",  # Search
            "tag",
        ),
        FieldSet(
            "prefixes",
            "ip_ranges",
            "ip_addresses",
            "devices",
            "virtual_machines",
            name="Aliased objects - all objects are OR'ed together, any will match",
        ),
    )
