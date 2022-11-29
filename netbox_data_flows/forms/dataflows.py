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

from netbox_data_flows.models import (
    Application,
    ApplicationRole,
    DataFlow,
)
from netbox_data_flows.choices import (
    DataFlowInheritedStatusChoices,
    DataFlowProtocolChoices,
    DataFlowStatusChoices,
)


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


class DataFlowFormBase(NetBoxModelForm):
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



class DataFlowEditForm(DataFlowFormBase):
    application = DynamicModelChoiceField(
        queryset=Application.objects.all(),
        help_text="Application that this data flow (and all of its descendants) is part of.",
    )
    parent = DynamicModelChoiceField(
        queryset=DataFlow.objects.all(),
        required=False,
        query_params={
            "application_id": "$application",
        },
        help_text="Direct parent of this Data Flow. Use it to create a hierarchy of data flows. Disabling a parent disables all its descendants.",
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
                "status",
                "parent",
                "tags",
            ),
        ),
        (
            "Specifications",
            (
                "protocol",
                "source_ports",
                "source_device",
                "source_virtual_machine",
                "source_prefix",
                "source_ipaddress",
                "destination_ports",
                "destination_device",
                "destination_virtual_machine",
                "destination_prefix",
                "destination_ipaddress",
            ),
        ),
    )

    class Meta:
        model = DataFlow
        fields = (
            "application",
            "name",
            "status",
            "parent",
            "comments",
            "tags",
            "protocol",
            "source_ports",
            "source_device",
            "source_virtual_machine",
            "source_prefix",
            "source_ipaddress",
            "destination_ports",
            "destination_device",
            "destination_virtual_machine",
            "destination_prefix",
            "destination_ipaddress",
        )
        widgets = {
            "protocol": StaticSelect(),
        }




#
# Bulk forms
#


class DataFlowBulkEditForm(NetBoxModelBulkEditForm):
    model = DataFlow

        queryset=DataFlow.objects.all(),
        required=False,
    )
    application = DynamicModelChoiceField(
        queryset=Application.objects.all(),
    )

    status = forms.ChoiceField(
        choices=add_blank_choice(DataFlowStatusChoices),
        required=False,
        widget=StaticSelect(),
    )
    protocol = forms.ChoiceField(
        choices=add_blank_choice(DataFlowProtocolChoices),
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
                "status",
                "parent",
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
        "parent",
        "protocol",
        "source_ports",
        "destination_ports",
    )


class DataFlowCSVForm(NetBoxModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=DataFlow.objects.all(),
        required=False,
        to_field_name="name",
    )
    application = CSVModelChoiceField(
        queryset=Application.objects.all(),
        to_field_name="name",
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
        model = DataFlow
        fields = (
            "application",
            "name",
            "status",
            "parent",
            "protocol",
            "source_ports",
            "destination_ports",
        )


#
# Filter forms
#


class DataFlowFilterFormBase(NetBoxModelFilterSetForm):
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


    class Meta:
        abstract = True


class DataFlowFilterForm(DataFlowFilterFormBase):
    model = DataFlow
    tag = TagFilterField(model)

    application = DynamicModelMultipleChoiceField(
        queryset=Application.objects.all(), required=False
    )
    application_role = DynamicModelMultipleChoiceField(
        queryset=ApplicationRole.objects.all(), required=False
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
