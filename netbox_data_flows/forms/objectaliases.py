from django import forms

from extras.models import Tag
from netbox.forms import PrimaryModelBulkEditForm, PrimaryModelFilterSetForm, PrimaryModelForm, PrimaryModelImportForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import CSVChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine

from netbox_data_flows import choices, models

__all__ = (
    "ObjectAliasForm",
    "ObjectAliasBulkEditForm",
    "ObjectAliasFilterForm",
    "ObjectAliasImportForm",
)

#
# Object forms
#


class ObjectAliasForm(PrimaryModelForm):
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
    device_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        selector=True,
        label="Device Tags",
        help_text="The IPs of the devices with this tag re dynamically added to this alias.",
    )
    virtual_machine_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        selector=True,
        label="Virtual Machine Tags",
        help_text="The IPs of the virtual machines with this tag re dynamically added to this alias.",
    )
    tag_matching_rule = forms.ChoiceField(
        choices=choices.TagMatchingRuleChoices,
        label="Tag matching rule",
        help_text="Select with IP of the devices and virtual machines are selected with the tags.",
        required=True,
    )

    fieldsets = (
        FieldSet(
            "name",
            "description",
            "tags",
        ),
        FieldSet(
            "prefixes",
            "ip_ranges",
            "ip_addresses",
            name="Aliased objects",
        ),
        FieldSet(
            "device_tags",
            "virtual_machine_tags",
            "tag_matching_rule",
            name="Tag matching",
        ),
    )

    class Meta:
        model = models.ObjectAlias
        fields = (
            "comments",
            "description",
            "device_tags",
            "ip_addresses",
            "ip_ranges",
            "name",
            "owner",
            "prefixes",
            "tag_matching_rule",
            "tags",
            "virtual_machine_tags",
        )


#
# Bulk forms
#


class ObjectAliasBulkEditForm(PrimaryModelBulkEditForm):
    model = models.ObjectAlias

    description = forms.CharField(max_length=200, required=False)

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
    device_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Device Tags",
    )
    virtual_machine_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Virtual Machine Tags",
    )
    tag_matching_rule = forms.ChoiceField(
        choices=add_blank_choice(choices.TagMatchingRuleChoices),
        label="Tag matching rule",
        required=False,
    )

    fieldsets = (
        FieldSet(
            "description",
            "comments",
        ),
        FieldSet(
            "prefixes",
            "ip_ranges",
            "ip_addresses",
            name="Aliased objects",
        ),
        FieldSet(
            "device_tags",
            "virtual_machine_tags",
            "tag_matching_rule",
            name="Tag matching",
        ),
    )
    nullable_fields = (
        "comments",
        "description",
        "device_tags",
        "owner",
        "prefixes",
        "ip_ranges",
        "ip_addresses",
        "virtual_machine_tags",
        "tag_matching_rule",
    )


class ObjectAliasImportForm(PrimaryModelImportForm):
    tag_matching_rule = CSVChoiceField(
        choices=add_blank_choice(choices.TagMatchingRuleChoices),
        required=True,
        help_text="Tag matching rule",
    )

    class Meta:
        model = models.ObjectAlias
        fields = (
            "name",
            "description",
            "owner",
            "comments",
            "tag_matching_rule",
            "tags",
        )


#
# Filter forms
#


class ObjectAliasFilterForm(PrimaryModelFilterSetForm):
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
    device_tags = TagFilterField(Device)
    virtual_machine_tags = TagFilterField(VirtualMachine)
    tag_matching_rule = forms.ChoiceField(
        choices=add_blank_choice(choices.TagMatchingRuleChoices),
        label="Tag matching rule",
        required=False,
    )

    fieldsets = (
        FieldSet(
            "filter_id",  # Saved Filter
            "q",  # Search
            "tag",
            "owner_id",
        ),
        FieldSet(
            "prefixes",
            "ip_ranges",
            "ip_addresses",
            "devices",
            "virtual_machines",
            name="Aliased objects - all objects are OR'ed together, any will match",
        ),
        FieldSet(
            "device_tags",
            "virtual_machine_tags",
            "tag_matching_rule",
            name="Tag matching",
        ),
    )
