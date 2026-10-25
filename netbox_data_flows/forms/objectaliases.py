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
        help_text="Dynamically select devices matching these tags using the machine tag operator.",
    )
    virtual_machine_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        selector=True,
        label="Virtual Machine Tags",
        help_text="Dynamically select virtual machines matching these tags using the machine tag operator.",
    )
    interface_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        selector=True,
        label="Interface Tags",
        help_text="Restrict dynamic IPs to interfaces with these tags; leave empty for no interface filter.",
    )
    interface_tag_operator = forms.ChoiceField(
        choices=choices.TagOperatorChoices,
        label="Interface tag operator",
        help_text="Match any or all tags on each interface.",
        required=True,
    )
    machine_tag_operator = forms.ChoiceField(
        choices=choices.TagOperatorChoices,
        label="Machine tag operator",
        help_text="Match any or all tags on each device or virtual machine.",
        required=True,
    )
    tag_matching_rule = forms.ChoiceField(
        choices=choices.TagMatchingRuleChoices,
        label="Tag matching rule",
        help_text="Select primary, OOB or all IPs, then apply the interface tag filter.",
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
            "machine_tag_operator",
            "tag_matching_rule",
            "interface_tags",
            "interface_tag_operator",
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
            "interface_tags",
            "interface_tag_operator",
            "machine_tag_operator",
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
    interface_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Interface Tags",
        help_text="Update the interface tag selector; use the clear option to remove it.",
    )
    interface_tag_operator = forms.ChoiceField(
        choices=add_blank_choice(choices.TagOperatorChoices),
        label="Interface tag operator",
        help_text="Match any or all tags on each interface.",
        required=False,
    )
    machine_tag_operator = forms.ChoiceField(
        choices=add_blank_choice(choices.TagOperatorChoices),
        label="Machine tag operator",
        help_text="Match any or all tags on each device or virtual machine.",
        required=False,
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
            "machine_tag_operator",
            "tag_matching_rule",
            "interface_tags",
            "interface_tag_operator",
            name="Tag matching",
        ),
    )
    nullable_fields = (
        "comments",
        "description",
        "device_tags",
        "interface_tags",
        "owner",
        "prefixes",
        "ip_ranges",
        "ip_addresses",
        "virtual_machine_tags",
        "tag_matching_rule",
    )


class ObjectAliasImportForm(PrimaryModelImportForm):
    interface_tag_operator = CSVChoiceField(
        choices=choices.TagOperatorChoices,
        required=False,
        help_text="Interface tag operator (any or all)",
    )
    machine_tag_operator = CSVChoiceField(
        choices=choices.TagOperatorChoices,
        required=False,
        help_text="Machine tag operator (any or all)",
    )
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
            "interface_tag_operator",
            "machine_tag_operator",
            "tag_matching_rule",
            "tags",
        )


#
# Filter forms
#


class ObjectAliasFilterForm(PrimaryModelFilterSetForm):
    model = models.ObjectAlias
    tag = TagFilterField(model)

    matching_type = forms.MultipleChoiceField(
        choices=choices.ObjectAliasMatchingChoices,
        label="Target matching type",
        required=False,
        help_text="Define how an object alias contains prefixes, ranges, addresses, devices and virtual machines.",
    )

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
    interface_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Interface Tags",
        help_text="Find aliases configured with these interface tags.",
    )
    interface_tag_operator = forms.ChoiceField(
        choices=add_blank_choice(choices.TagOperatorChoices),
        label="Interface tag operator",
        help_text="Match any or all tags on each interface.",
        required=False,
    )
    machine_tag_operator = forms.ChoiceField(
        choices=add_blank_choice(choices.TagOperatorChoices),
        label="Machine tag operator",
        help_text="Match any or all tags on each device or virtual machine.",
        required=False,
    )
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
            "matching_type",
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
            "machine_tag_operator",
            "tag_matching_rule",
            "interface_tags",
            "interface_tag_operator",
            name="Tag matching",
        ),
    )
