from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelImportForm,
    NetBoxModelFilterSetForm,
)
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    CSVModelMultipleChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    NumericArrayField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet

from dcim.models import Device
from ipam.models import Prefix, IPRange, IPAddress
from ipam.constants import SERVICE_PORT_MIN, SERVICE_PORT_MAX
from virtualization.models import VirtualMachine

from netbox_data_flows import models, choices


__all__ = (
    "DataFlowForm",
    "DataFlowBulkEditForm",
    "DataFlowImportForm",
    "DataFlowFilterForm",
)

#
# Object forms
#


class DataFlowForm(NetBoxModelForm):
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
        help_text=(
            "Group of this Data Flow. "
            "Disabling the group will disable this data flow."
        ),
    )

    comments = CommentField()
    source_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text=(
            "Comma-separated list of one or more port numbers. "
            "A range may be specified using a hyphen."
        ),
        required=False,
    )
    destination_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text=(
            "Comma-separated list of one or more port numbers. "
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
            "name",
            "description",
            "status",
            "tags",
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

    class Meta:
        model = models.DataFlow
        fields = (
            "application",
            "group",
            "name",
            "description",
            "status",
            "comments",
            "tags",
            "protocol",
            "source_ports",
            "destination_ports",
            "sources",
            "destinations",
        )
        help_texts = {
            "status": (
                "Status of the data group. If its group is disabled, "
                "the data flow will also be disabled."
            )
        }


#
# Bulk forms
#


class DataFlowBulkEditForm(NetBoxModelBulkEditForm):
    model = models.DataFlow

    description = forms.CharField(max_length=200, required=False)
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
    comments = CommentField()

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowProtocolChoices),
        required=False,
    )
    source_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text=(
            "Comma-separated list of one or more port numbers. "
            "A range may be specified using a hyphen."
        ),
        required=False,
    )
    destination_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text=(
            "Comma-separated list of one or more port numbers. "
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
        "group",
        "description",
        "comments",
        "protocol",
        "source_ports",
        "destination_ports",
        "sources",
        "destinations",
    )


class DataFlowImportForm(NetBoxModelImportForm):
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
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text=(
            "Comma-separated list of one or more port numbers. "
            "A range may be specified using a hyphen."
        ),
        required=False,
    )
    destination_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text=(
            "Comma-separated list of one or more port numbers. "
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
            "description",
            "status",
            "protocol",
            "source_ports",
            "destination_ports",
            "sources",
            "destinations",
            "comments",
        )


#
# Filter forms
#


class DataFlowFilterForm(NetBoxModelFilterSetForm):
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
        min_value=SERVICE_PORT_MIN,
        max_value=SERVICE_PORT_MAX,
        required=False,
        help_text="Use the API or repeat the URL parameter to select several",
    )
    destination_ports = forms.IntegerField(
        min_value=SERVICE_PORT_MIN,
        max_value=SERVICE_PORT_MAX,
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
    source_ipranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="Source IP Ranges",
    )
    source_ipaddresses = DynamicModelMultipleChoiceField(
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
    destination_ipranges = DynamicModelMultipleChoiceField(
        queryset=IPRange.objects.all(),
        required=False,
        label="Destination IP Ranges",
    )
    destination_ipaddresses = DynamicModelMultipleChoiceField(
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

    fieldsets = (
        FieldSet(
            "filter_id",  # Saved Filter
            "q",  # Search
            "tag",
        ),
        FieldSet(
            "application_id",
            "application_role_id",
            "group_id",
            "recursive_group_id",
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
            "source_ipranges",
            "source_ipaddresses",
            "source_devices",
            "source_virtual_machines",
            name="Sources - all sources are OR'ed together, any will match",
        ),
        FieldSet(
            "destination_is_null",
            "destination_aliases",
            "destination_prefixes",
            "destination_ipranges",
            "destination_ipaddresses",
            "destination_devices",
            "destination_virtual_machines",
            name=(
                "Destinations - all destinations are OR'ed together, "
                "any will match"
            ),
        ),
    )
