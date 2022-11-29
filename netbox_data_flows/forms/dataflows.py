from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelCSVForm,
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
    "DataFlowCreateForm",
    "DataFlowEditForm",
    "DataFlowBulkEditForm",
    "DataFlowCSVForm",
    "DataFlowFilterForm",
)

#
# Object forms
#


class DataFlowForm(NetBoxModelForm):
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        help_text="Application that this data flow is part of.",
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

    # TODO:
    # sources
    # destinations

    fieldsets = (
        (
            "Data Flow",
            (
                "application",
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
            ),
        ),
    )

    class Meta:
        model = models.DataFlow
        fields = (
            "application",
            "name",
            "description",
            "status",
            "comments",
            "tags",
            "protocol",
            "source_ports",
            "destination_ports",
        )
        widgets = {
            "protocol": StaticSelect(),
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

    # TODO:
    # sources
    # destinations

    fieldsets = (
        (
            "Data Flow",
            (
                "application",
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
            ),
        ),
    )
    nullable_fields = (
        "application",
        "description",
        "protocol",
        "source_ports",
        "destination_ports",
    )


class DataFlowCSVForm(NetBoxModelCSVForm):
    application = CSVModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
        to_field_name="name",
    )
    )
    status = CSVChoiceField(
        choices=add_blank_choice(DataFlowStatusChoices),
        required=True,
    )
    protocol = CSVChoiceField(
        choices=add_blank_choice(DataFlowStatusChoices),
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

    application = DynamicModelMultipleChoiceField(
        queryset=models.Application.objects.all(), required=False
    )
    application_role = DynamicModelMultipleChoiceField(
        queryset=models.ApplicationRole.objects.all(), required=False
    )
    tag = TagFilterField(model)

    status = forms.ChoiceField(
        choices=add_blank_choice(DataFlowStatusChoices),
        required=False,
        widget=StaticSelect(),
    )
    inherited_status = forms.ChoiceField(
        choices=add_blank_choice(DataFlowStatusChoices),
        required=False,
        widget=StaticSelect(),
    )
    protocol = MultipleChoiceField(
        choices=add_blank_choice(DataFlowProtocolChoices),
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

    # TODO:
    # sources
    # destinations

    fieldsets = (
        (
            None,
            (
                "application",
                "application_role",
                "status",
                "inherited_status",
                "tag",
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
        # (
        #     "Source (Any matching)",
        #     (
        #         "source_device",
        #         "source_virtual_machine",
        #         "source_prefix",
        #         "source_ipaddress",
        #     ),
        # ),
        # (
        #     "Destination (Any matching)",
        #     (
        #         "destination_device",
        #         "destination_virtual_machine",
        #         "destination_prefix",
        #         "destination_ipaddress",
        #     ),
        # ),
    )
