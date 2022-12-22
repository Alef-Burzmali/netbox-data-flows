from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelImportForm,
    NetBoxModelFilterSetForm,
)
from utilities.forms import (
    add_blank_choice,
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    MultipleChoiceField,
    NumericArrayField,
    StaticSelect,
    TagFilterField,
)

from dcim.models import Device
from ipam.constants import SERVICE_PORT_MIN, SERVICE_PORT_MAX
from ipam.models import Prefix, IPAddress
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
        help_text="Application that this data flow is part of.",
    )
    group = DynamicModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        query_params={
            "application_id": "$application",
        },
        help_text="Parent group of this Data Flow. Disabling the group will disable this data flow.",
    )

    comments = CommentField()
    source_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen.",
        required=False,
    )
    destination_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen.",
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
        widgets = {
            "protocol": StaticSelect(),
        }
        help_texts = {
            "status": "Status of the data group. If its group is disabled, the data flow will also be disabled."
        }


#
# Bulk forms
#


class DataFlowBulkEditForm(NetBoxModelBulkEditForm):
    model = models.DataFlow

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

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
        widget=StaticSelect(),
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowProtocolChoices),
        required=False,
        widget=StaticSelect(),
    )
    source_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen.",
        required=False,
    )
    destination_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen.",
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
    )
    status = CSVChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=True,
    )
    protocol = CSVChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )
    source_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen.",
        required=False,
    )
    destination_ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX
        ),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen.",
        required=False,
    )

    # TODO:
    # sources
    # destinations

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
        widget=StaticSelect(),
        help_text="Status of the data flows themselves",
    )
    inherited_status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
        widget=StaticSelect(),
        help_text="Status inherited from the data flow groups",
    )

    protocol = MultipleChoiceField(
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

    sources = DynamicModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
        label="Sources",
        help_text="Source object aliases",
    )
    destinations = DynamicModelMultipleChoiceField(
        queryset=models.ObjectAlias.objects.all(),
        required=False,
        label="Destinations",
        help_text="Destination object aliases",
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
                "sources",
                "destinations",
            ),
        ),
    )
