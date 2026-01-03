from django import forms

from netbox.forms import PrimaryModelBulkEditForm, PrimaryModelFilterSetForm, PrimaryModelForm, PrimaryModelImportForm
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    CSVChoiceField,
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, TabbedGroups

from dcim.models import Device
from ipam.models import IPAddress, IPRange, Prefix
from tenancy.forms import TenancyFilterForm, TenancyForm
from tenancy.models import Tenant
from virtualization.models import VirtualMachine

from netbox_data_flows import choices, models
from netbox_data_flows.constants import DATAFLOW_PORT_MAX, DATAFLOW_PORT_MIN

from .fields import IcmpTypeChoiceField, NumericArrayField, PlaceholderModelMultipleChoiceField


__all__ = (
    "DataFlowForm",
    "DataFlowBulkEditForm",
    "DataFlowImportForm",
    "DataFlowFilterForm",
)


#
# Object forms
#


def _port_selection():
    """Hack to force a deterministic ID for the tabs."""
    group = TabbedGroups(
        FieldSet("source_ports", "destination_ports", name="Ports"),
        FieldSet("icmpv4_types", name="ICMPv4 types"),
        FieldSet("icmpv6_types", name="ICMPv6 types"),
    )
    group.id = "port_selection"
    return group


class DataFlowForm(TenancyForm, PrimaryModelForm):
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
        selector=True,
        help_text="Application that this data flow is part of.",
    )
    group = DynamicModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        selector=True,
        help_text="Group of this Data Flow. Disabling the group will disable this data flow.",
    )

    sources = PlaceholderModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
        placeholder="Any",
    )
    destinations = PlaceholderModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
        placeholder="Any",
    )

    protocol = forms.ChoiceField(
        choices=choices.DataFlowProtocolChoices,
        label="Protocol",
        required=True,
    )

    source_ports = NumericArrayField(
        base_field=forms.IntegerField(min_value=DATAFLOW_PORT_MIN, max_value=DATAFLOW_PORT_MAX),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen.",
        required=False,
    )
    destination_ports = NumericArrayField(
        base_field=forms.IntegerField(min_value=DATAFLOW_PORT_MIN, max_value=DATAFLOW_PORT_MAX),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen.",
        required=False,
    )

    # replaces the destination ports
    icmpv4_types = IcmpTypeChoiceField(
        choices=choices.ICMPv4TypeChoices,
        label="ICMPv4 Types",
        help_text="One or more ICMPv4 types. Leave empty for any.",
        required=False,
        placeholder="Any",
    )
    icmpv6_types = IcmpTypeChoiceField(
        choices=choices.ICMPv6TypeChoices,
        label="ICMPv6 Types",
        help_text="One or more ICMPv6 types. Leave empty for any.",
        required=False,
        placeholder="Any",
    )

    fieldsets = (
        FieldSet(
            "application",
            "group",
            "name",
            "description",
            "status",
            "tags",
        ),
        FieldSet(
            "tenant_group",
            "tenant",
            name="Tenancy",
        ),
        FieldSet(
            "sources",
            "destinations",
            "protocol",
            _port_selection(),
            name="Specifications",
        ),
    )

    class Meta:
        model = models.DataFlow
        fields = (
            "application",
            "comments",
            "description",
            "destination_ports",
            "destinations",
            "group",
            "icmpv4_types",
            "icmpv6_types",
            "name",
            "owner",
            "protocol",
            "source_ports",
            "sources",
            "status",
            "tags",
            "tenant",
        )
        help_texts = {
            "status": "Status of the data group. If its group is disabled, the data flow will also be disabled."
        }

    def __init__(self, instance=None, initial=None, *args, **kwargs):
        if instance:
            if not initial:
                initial = dict()

            if instance.protocol == choices.DataFlowProtocolChoices.PROTOCOL_ICMPv4:
                initial["icmpv4_types"] = instance.destination_ports or []
            elif instance.protocol == choices.DataFlowProtocolChoices.PROTOCOL_ICMPv6:
                initial["icmpv6_types"] = instance.destination_ports or []

        super().__init__(instance=instance, initial=initial, *args, **kwargs)

    def clean(self):
        # Save ICMPv4 and ICMPv6 types as destination ports

        cleaned_data = super().clean()
        if not cleaned_data:
            cleaned_data = self.cleaned_data

        protocol = cleaned_data.get("protocol")
        cleaned_data = cleaned_data.copy()

        if protocol == choices.DataFlowProtocolChoices.PROTOCOL_ICMPv4:
            source_ports = []
            destination_ports = cleaned_data.get("icmpv4_types")
        elif protocol == choices.DataFlowProtocolChoices.PROTOCOL_ICMPv6:
            source_ports = []
            destination_ports = cleaned_data.get("icmpv6_types")
        else:
            source_ports = cleaned_data.get("source_ports")
            destination_ports = cleaned_data.get("destination_ports")

        cleaned_data["source_ports"] = source_ports
        cleaned_data["destination_ports"] = destination_ports
        return cleaned_data


#
# Bulk forms
#


class DataFlowBulkEditForm(PrimaryModelBulkEditForm):
    model = models.DataFlow

    description = forms.CharField(
        max_length=500,  # Overwritten from default 200
        required=False,
    )
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
    )
    group = DynamicModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        query_params={
            "application_id": "$application",
        },
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowProtocolChoices),
        required=False,
    )
    source_ports = NumericArrayField(
        base_field=forms.IntegerField(min_value=DATAFLOW_PORT_MIN, max_value=DATAFLOW_PORT_MAX),
        help_text=(
            "Comma-separated list of one or more port numbers (leave empty for ICMP types). "
            "A range may be specified using a hyphen."
        ),
        required=False,
    )
    destination_ports = NumericArrayField(
        base_field=forms.IntegerField(min_value=DATAFLOW_PORT_MIN, max_value=DATAFLOW_PORT_MAX),
        help_text=(
            "Comma-separated list of one or more port numbers or ICMP type numerical values. "
            "A range may be specified using a hyphen."
        ),
        required=False,
    )

    sources = DynamicModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
    )
    destinations = DynamicModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
    )

    fieldsets = (
        FieldSet(
            "application",
            "group",
            "description",
            "status",
            "tenant",
        ),
        FieldSet(
            "protocol",
            "source_ports",
            "destination_ports",
            "sources",
            "destinations",
            name="Specifications",
        ),
    )
    nullable_fields = (
        "application",
        "description",
        "comments",
        "destination_ports",
        "destinations",
        "group",
        "owner",
        "protocol",
        "source_ports",
        "sources",
        "tenant",
    )


class DataFlowImportForm(PrimaryModelImportForm):
    application = CSVModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Application",
    )
    group = CSVModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        help_text="Data flow group",
        to_field_name="slug",
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Assigned tenant",
    )
    status = CSVChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=True,
        help_text="Status",
    )
    protocol = CSVChoiceField(
        choices=add_blank_choice(choices.DataFlowProtocolChoices),
        required=True,
        help_text="Protocol",
    )
    source_ports = NumericArrayField(
        base_field=forms.IntegerField(min_value=DATAFLOW_PORT_MIN, max_value=DATAFLOW_PORT_MAX),
        help_text=(
            "Comma-separated list of one or more port numbers (leave empty for ICMP types). "
            "A range may be specified using a hyphen."
        ),
        required=False,
    )
    destination_ports = NumericArrayField(
        base_field=forms.IntegerField(min_value=DATAFLOW_PORT_MIN, max_value=DATAFLOW_PORT_MAX),
        help_text=(
            "Comma-separated list of one or more port numbers or ICMP type numerical values. "
            "A range may be specified using a hyphen."
        ),
        required=False,
    )

    sources = CSVModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Comma-separated list of one or more name of ObjectAlias.",
    )
    destinations = CSVModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Comma-separated list of one or more name of ObjectAlias.",
    )

    class Meta:
        model = models.DataFlow
        fields = (
            "application",
            "group",
            "name",
            "tenant",
            "description",
            "status",
            "protocol",
            "source_ports",
            "destination_ports",
            "sources",
            "destinations",
            "owner",
            "comments",
            "tags",
        )


#
# Filter forms
#


class DataFlowFilterForm(TenancyFilterForm, PrimaryModelFilterSetForm):
    model = models.DataFlow

    application_id = DynamicModelMultipleChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
        label="Application",
        help_text="Application(s) that the data flows are part of",
    )
    application_role_id = DynamicModelMultipleChoiceField(
        queryset=models.ApplicationRole.objects.all(),
        required=False,
        label="Application Role",
        help_text="Application Role(s) that the data flows are part of",
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        label="Direct parent group",
        help_text="Direct group(s) of the data flows",
    )
    recursive_group_id = DynamicModelMultipleChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        label="Ancestor group",
        help_text="Parent or ancestor group(s) of the data flows",
    )
    tag = TagFilterField(model)

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
        help_text="Status of the data flows themselves",
    )
    inherited_status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
        help_text="Status inherited from the ancestor groups",
    )

    protocol = forms.MultipleChoiceField(
        choices=choices.DataFlowProtocolChoices,
        required=False,
    )
    source_ports = forms.IntegerField(
        min_value=DATAFLOW_PORT_MIN,
        max_value=DATAFLOW_PORT_MAX,
        required=False,
        help_text="Use the API or repeat the URL parameter to select several",
    )
    destination_ports = forms.IntegerField(
        min_value=DATAFLOW_PORT_MIN,
        max_value=DATAFLOW_PORT_MAX,
        required=False,
        help_text="Use the API or repeat the URL parameter to select several",
    )

    source_is_null = forms.ChoiceField(
        choices=add_blank_choice(choices.TargetIsEmptyChoice),
        required=False,
        help_text="No sources are defined?",
    )
    source_aliases = DynamicModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
        label="Source Object Aliases",
    )
    source_prefixes = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Source Prefixes",
    )
    source_ip_ranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="Source IP Ranges",
    )
    source_ip_addresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Source IP Addresses",
    )
    source_devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Source Devices",
        help_text="Any IP addresses of the device",
    )
    source_virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Source Virtual Machines",
        help_text="Any IP address of the virtual machine",
    )

    destination_is_null = forms.ChoiceField(
        choices=add_blank_choice(choices.TargetIsEmptyChoice),
        required=False,
        help_text="No destinations are defined?",
    )
    destination_aliases = DynamicModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
        label="Destination Object Aliases",
    )
    destination_prefixes = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Destination Prefixes",
    )
    destination_ip_ranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="Destination IP Ranges",
    )
    destination_ip_addresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Destination IP Addresses",
    )
    destination_devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Destination Devices",
        help_text="Any IP addresses of the device",
    )
    destination_virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Destination Virtual Machines",
        help_text="Any IP address of the virtual machine",
    )

    selector_fields = ("filter_id", "q", "application_id", "recursive_group_id")
    fieldsets = (
        FieldSet(
            "filter_id",  # Saved Filter
            "q",  # Search
            "tag",
            "owner_id",
        ),
        FieldSet(
            "application_id",
            "application_role_id",
            "group_id",
            "recursive_group_id",
        ),
        FieldSet(
            "tenant_group_id",
            "tenant_id",
            name="Tenancy",
        ),
        FieldSet(
            "status",
            "inherited_status",
            name="Status",
        ),
        FieldSet(
            "protocol",
            "source_ports",
            "destination_ports",
            name="Specifications",
        ),
        FieldSet(
            "source_is_null",
            "source_aliases",
            "source_prefixes",
            "source_ip_ranges",
            "source_ip_addresses",
            "source_devices",
            "source_virtual_machines",
            name="Sources - all sources are OR'ed together, any will match",
        ),
        FieldSet(
            "destination_is_null",
            "destination_aliases",
            "destination_prefixes",
            "destination_ip_ranges",
            "destination_ip_addresses",
            "destination_devices",
            "destination_virtual_machines",
            name="Destinations - all destinations are OR'ed together, any will match",
        ),
    )
