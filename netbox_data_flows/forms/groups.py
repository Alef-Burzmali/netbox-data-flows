from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
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

from netbox_data_flows import models, choices


__all__ = (
    "DataFlowGroupForm",
    "DataFlowGroupBulkEditForm",
    "DataFlowGroupImportForm",
)

#
# Object forms
#


class DataFlowGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        help_text="Direct parent of this Data Flow Group. Use it to create a hierarchy of data flows. Disabling a parent disables all its descendants.",
    )
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
        help_text="Application that this data flow group (and all of its descendants) is part of.",
    )
    comments = CommentField()

    fieldsets = (
        (
            "Data Flow Group",
            (
                "application",
                "parent",
                "name",
                "description",
                "status",
                "tags",
            ),
        ),
    )

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "application",
            "parent",
            "name",
            "description",
            "status",
            "comments",
            "tags",
        )


#
# Bulk forms
#


class DataFlowGroupBulkEditForm(NetBoxModelBulkEditForm):
    model = models.DataFlowGroup

    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
    )
    parent = DynamicModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
    )

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
        widget=StaticSelect(),
    )

    fieldsets = (
        (
            "Data Flow Groups",
            (
                "application",
                "parent",
                "name",
                "description",
                "status",
                "tags",
            ),
        ),
    )
    nullable_fields = (
        "parent",
        "application",
    )


class DataFlowGroupImportForm(NetBoxModelImportForm):
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
    )
    parent = CSVModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        to_field_name="name",
    )
    status = CSVChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "name",
            "description",
            "application",
            "parent",
            "status",
        )


#
# Filter forms
#


class DataFlowGroupFilterForm(NetBoxModelFilterSetForm):
    model = models.DataFlowGroup

    tag = TagFilterField(model)

    application = DynamicModelMultipleChoiceField(
        queryset=models.Application.objects.all(), required=False
    )
    application_role = DynamicModelMultipleChoiceField(
        queryset=models.ApplicationRole.objects.all(), required=False
    )
    ancestor = DynamicModelMultipleChoiceField(
        queryset=models.DataFlowGroup.objects.all(), required=False
    )

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
        widget=StaticSelect(),
    )
    inherited_status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
        widget=StaticSelect(),
    )

    fieldsets = (
        (
            None,
            (
                "application",
                "application_role",
                "ancestor",
                "status",
                "inherited_status",
                "tag",
            ),
        ),
    )
