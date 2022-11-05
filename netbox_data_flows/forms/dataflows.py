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
    DataFlowTemplate,
)
from netbox_data_flows.choices import (
    DataFlowInheritedStatusChoices,
    DataFlowProtocolChoices,
    DataFlowStatusChoices,
)


__all__ = (
    "DataFlowCreateForm",
    "DataFlowEditForm",
    "DataFlowTemplateForm",
    "DataFlowBulkEditForm",
    "DataFlowCSVForm",
    "DataFlowTemplateBulkEditForm",
    "DataFlowTemplateCSVForm",
    "DataFlowFilterForm",
    "DataFlowTemplateFilterForm",
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

    source_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        help_text="Source Device (HW) of the Data Flow. Only one device and only one type of source can be selected per Data Flow.",
    )
    source_virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        help_text="Source Virtual Machine of the Data Flow. Only one VM and only one type of source can be selected per Data Flow.",
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text="Source IP Prefix of the Data Flow. Only one prefix and only one type of source can be selected per Data Flow.",
    )
    source_ipaddress = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Source IP Address",
        help_text="Source IP Address of the Data Flow. Only one address and only one type of source can be selected per Data Flow.",
    )

    destination_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        help_text="Destination Device (HW) of the Data Flow. Only one device and only one type of destination can be selected per Data Flow.",
    )
    destination_virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        help_text="Destination Virtual Machine of the Data Flow. Only one VM and only one type of destination can be selected per Data Flow.",
    )
    destination_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text="Destination IP Prefix of the Data Flow. Only one prefix and only one type of destination can be selected per Data Flow.",
    )
    destination_ipaddress = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Destination IP Address",
        help_text="Destination IP Address of the Data Flow. Only one address and only one type of destination can be selected per Data Flow.",
    )

    class Meta:
        abstract = True


class DataFlowTemplateForm(DataFlowFormBase):
    parent = DynamicModelChoiceField(
        queryset=DataFlowTemplate.objects.all(),
        required=False,
        help_text="Direct parent of this Data Flow. Use it to create a hierarchy of data flows. Disabling a parent disables all its descendants. Cloning a template clones all its descendants.",
    )

    fieldsets = (
        (
            "Data Flow Template",
            (
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
        model = DataFlowTemplate
        fields = (
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
        model = DataFlowTemplate
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


class DataFlowCreateForm(DataFlowEditForm):
    dataflow_template = DynamicModelChoiceField(
        queryset=DataFlowTemplate.objects.all(),
        required=False,
        help_text=(
            "Template to use as base for this Data Flow. "
            "You will be able to edit the specifications of the new Data Flow after saving. "
            "If this template has children, they will be cloned too."
        ),
    )

    class Meta:
        model = DataFlowTemplate
        fields = (
            "dataflow_template",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields which may be populated from a DataFlowTemplate are not required
        for field in (
            "name",
            "status",
        ):
            self.fields[field].required = False
            del self.fields[field].widget.attrs["required"]

    def clean(self):
        super().clean()

        if self.cleaned_data["dataflow_template"]:
            # Create a new DataFlow from the specified template
            dataflow_template = self.cleaned_data["dataflow_template"]

            for field in (
                "name",
                "status",
                "comments",
                "protocol",
                "source_ports",
                "destination_ports",
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
            ):
                if not self.cleaned_data[field]:
                    self.cleaned_data[field] = getattr(
                        dataflow_template, field
                    )

        elif not all(self.cleaned_data[f] for f in ("name", "status")):
            raise forms.ValidationError(
                "Must specify name and status if not using a template."
            )


#
# Bulk forms
#


class DataFlowTemplateBulkEditForm(NetBoxModelBulkEditForm):
    model = DataFlowTemplate

    parent = DynamicModelChoiceField(
        queryset=DataFlowTemplate.objects.all(),
        required=False,
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

    source_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        help_text="Source Device (HW) of the Data Flow. Only one device and only one type of source can be selected per Data Flow.",
    )
    source_virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        help_text="Source Virtual Machine of the Data Flow. Only one VM and only one type of source can be selected per Data Flow.",
    )
    source_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text="Source IP Prefix of the Data Flow. Only one prefix and only one type of source can be selected per Data Flow.",
    )
    source_ipaddress = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Source IP Address",
        help_text="Source IP Address of the Data Flow. Only one address and only one type of source can be selected per Data Flow.",
    )

    destination_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        help_text="Destination Device (HW) of the Data Flow. Only one device and only one type of destination can be selected per Data Flow.",
    )
    destination_virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        help_text="Destination Virtual Machine of the Data Flow. Only one VM and only one type of destination can be selected per Data Flow.",
    )
    destination_prefix = DynamicModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        help_text="Destination IP Prefix of the Data Flow. Only one prefix and only one type of destination can be selected per Data Flow.",
    )
    destination_ipaddress = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Destination IP Address",
        help_text="Destination IP Address of the Data Flow. Only one address and only one type of destination can be selected per Data Flow.",
    )

    fieldsets = (
        (
            "Data Flow Template",
            (
                "status",
                "parent",
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
    nullable_fields = (
        "parent",
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


class DataFlowBulkEditForm(DataFlowTemplateBulkEditForm):
    model = DataFlow

    application = DynamicModelChoiceField(
        queryset=Application.objects.all(),
        required=False,
    )
    parent = DynamicModelChoiceField(
        queryset=DataFlow.objects.all(),
        required=False,
    )

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
    nullable_fields = (
        "parent",
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


class DataFlowTemplateCSVForm(NetBoxModelCSVForm):
    parent = CSVModelChoiceField(
        queryset=DataFlowTemplate.objects.all(),
        required=False,
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

    source_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Source Device (HW) of the Data Flow. Only one device and only one type of source can be selected per Data Flow.",
    )
    source_virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Source Virtual Machine of the Data Flow. Only one VM and only one type of source can be selected per Data Flow.",
    )
    source_prefix = CSVModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Source IP Prefix of the Data Flow. Only one prefix and only one type of source can be selected per Data Flow.",
    )
    source_ipaddress = CSVModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        to_field_name="name",
        label="Source IP Address",
        help_text="Source IP Address of the Data Flow. Only one address and only one type of source can be selected per Data Flow.",
    )

    destination_device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Destination Device (HW) of the Data Flow. Only one device and only one type of destination can be selected per Data Flow.",
    )
    destination_virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Destination Virtual Machine of the Data Flow. Only one VM and only one type of destination can be selected per Data Flow.",
    )
    destination_prefix = CSVModelChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        to_field_name="name",
        help_text="Destination IP Prefix of the Data Flow. Only one prefix and only one type of destination can be selected per Data Flow.",
    )
    destination_ipaddress = CSVModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        to_field_name="name",
        label="Destination IP Address",
        help_text="Destination IP Address of the Data Flow. Only one address and only one type of destination can be selected per Data Flow.",
    )

    class Meta:
        model = DataFlow
        fields = (
            "name",
            "status",
            "parent",
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


class DataFlowCSVForm(DataFlowTemplateCSVForm):
    application = CSVModelChoiceField(
        queryset=Application.objects.all(),
        required=True,
        to_field_name="name",
    )
    parent = CSVModelChoiceField(
        queryset=DataFlow.objects.all(),
        required=False,
        to_field_name="name",
    )

    class Meta:
        model = DataFlow
        fields = (
            "application",
            "name",
            "status",
            "parent",
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

    source_device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Source devices",
    )
    source_virtual_machine = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Source virtual machines",
    )
    source_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Source prefixes",
    )
    source_ipaddress = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Source IP Addresses",
    )

    destination_device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Destination devices",
    )
    destination_virtual_machine = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Destination virtual machines",
    )
    destination_prefix = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        label="Destination prefixes",
    )
    destination_ipaddress = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="Destination IP Addresses",
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
        (
            "Source (Any matching)",
            (
                "source_device",
                "source_virtual_machine",
                "source_prefix",
                "source_ipaddress",
            ),
        ),
        (
            "Destination (Any matching)",
            (
                "destination_device",
                "destination_virtual_machine",
                "destination_prefix",
                "destination_ipaddress",
            ),
        ),
    )


class DataFlowTemplateFilterForm(DataFlowFilterFormBase):
    model = DataFlowTemplate
    tag = TagFilterField(model)

    fieldsets = (
        (
            "Data Flow Template",
            (
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
        (
            "Source (Any matching)",
            (
                "source_device",
                "source_virtual_machine",
                "source_prefix",
                "source_ipaddress",
            ),
        ),
        (
            "Destination (Any matching)",
            (
                "destination_device",
                "destination_virtual_machine",
                "destination_prefix",
                "destination_ipaddress",
            ),
        ),
    )
