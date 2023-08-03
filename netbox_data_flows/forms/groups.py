from django import forms

from netbox.forms import (
    NetBoxModelForm,
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelImportForm,
)
from utilities.forms import add_blank_choice
from utilities.forms.fields import (
    CommentField,
    CSVChoiceField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    SlugField,
    TagFilterField,
)

from netbox_data_flows import models, choices


__all__ = (
    "DataFlowGroupForm",
    "DataFlowGroupBulkEditForm",
    "DataFlowGroupFilterForm",
    "DataFlowGroupImportForm",
)

#
# Object forms
#


class DataFlowGroupForm(NetBoxModelForm):
    slug = SlugField()
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
        selector=True,
        help_text="Application that this data flow group is related to.",
    )
    parent = DynamicModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        selector=True,
        help_text="Parent group of this Data Flow Group.",
    )
    comments = CommentField()

    fieldsets = (
        (
            "Data Flow Group",
            (
                "application",
                "parent",
                "name",
                "slug",
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
            "slug",
            "description",
            "status",
            "comments",
            "tags",
        )
        help_texts = {
            "status": (
                "Status of the data flow group. Disabling a parent disables "
                "all its descendants and their data flows."
            )
        }


#
# Bulk forms
#


class DataFlowGroupBulkEditForm(NetBoxModelBulkEditForm):
    model = models.DataFlowGroup

    description = forms.CharField(max_length=200, required=False)
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
        selector=True,
    )
    parent = DynamicModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        selector=True,
    )
    comments = CommentField()

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )

    fieldsets = (
        (
            "Data Flow Groups",
            (
                "application",
                "parent",
                "description",
                "status",
            ),
        ),
    )
    nullable_fields = (
        "parent",
        "application",
        "comments",
    )


class DataFlowGroupImportForm(NetBoxModelImportForm):
    application = DynamicModelChoiceField(
        queryset=models.Application.objects.all(),
        required=False,
    )
    parent = CSVModelChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        to_field_name="slug",
    )
    status = CSVChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )

    class Meta:
        model = models.DataFlowGroup
        fields = (
            "name",
            "slug",
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
    parent_id = DynamicModelMultipleChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        label="Parent group",
        help_text="Direct parent group(s)",
    )
    ancestor_id = DynamicModelMultipleChoiceField(
        queryset=models.DataFlowGroup.objects.all(),
        required=False,
        label="Ancestor group",
        help_text="Recursive parent group(s)",
    )

    status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
    )
    inherited_status = forms.ChoiceField(
        choices=add_blank_choice(choices.DataFlowStatusChoices),
        required=False,
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
                "application",
                "application_role",
                "parent_id",
                "ancestor_id",
            ),
        ),
        (
            "Status",
            (
                "status",
                "inherited_status",
            ),
        ),
    )
