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
            "Parent group of this Data Flow. "
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
        (
            "Data Flow",
            (
                "application",
                "group",
                "name",
                "description",
                "status",
                "tags",
            ),
        ),
        (
            "Specifications",
            (
                "protocol",
                "source_ports",
                "destination_ports",
                "sources",
                "destinations",
            ),
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
        (
            "Data Flow",
            (
                "application",
                "group",
                "description",
                "status",
            ),
        ),
        (
            "Specifications",
            (
                "protocol",
                "source_ports",
                "destination_ports",
                "sources",
                "destinations",
            ),
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
    )
    protocol = CSVChoiceField(
        choices=add_blank_choice(choices.DataFlowProtocolChoices),
        required=True,
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
        label="Direct group",
        help_text="Direct group(s)",
    )
    recursive_group_id = DynamicModelMultipleChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        label="Recursive group",
        help_text="Recursive group(s)",
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
        help_text="Status inherited from the data flow groups",
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
        (
            None,
            (
                "filter_id",  # Saved Filter
                "q",  # Search
                "tag",
            ),
        ),
        (
            None,
            (
                "application_id",
                "application_role_id",
                "group_id",
                "recursive_group_id",
            ),
        ),
        (
            "Status",
            (
                "status",
                "inherited_status",
            ),
        ),
        (
            "Specifications",
            (
                "protocol",
                "source_ports",
                "destination_ports",
            ),
        ),
        (
            "Sources - all sources are OR'ed together, any will match",
            (
                "source_is_null",
                "source_aliases",
                "source_prefixes",
                "source_ipranges",
                "source_ipaddresses",
                "source_devices",
                "source_virtual_machines",
            ),
        ),
        (
            (
                "Destinations - all destinations are OR'ed together, "
                "any will match"
            ),
            (
                "destination_is_null",
                "destination_aliases",
                "destination_prefixes",
                "destination_ipranges",
                "destination_ipaddresses",
                "destination_devices",
                "destination_virtual_machines",
            ),
        ),
    )
