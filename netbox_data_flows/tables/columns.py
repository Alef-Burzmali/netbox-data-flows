import django_tables2 as tables
from django.utils.safestring import mark_safe

from netbox.tables import columns
from utilities.data import array_to_string

from netbox_data_flows.utils.helpers import object_list_to_string


class ChoiceVirtualColumn(tables.Column):
    """Render a badge column based on a virtual field value.

    The choiceset must be passed as parameter.
    """

    def __init__(self, *args, choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.choices = choices

    def render(self, record, bound_column, value):
        if value in self.empty_values:
            return self.default

        for choice, display, color in self.choices.CHOICES:
            if choice == value:
                break

        return mark_safe(f'<span class="badge text-bg-{color}">{display}</span>')

    def value(self, value):
        return value


class PortListColumn(tables.Column):
    """
    Display a Port List.

    If empty, is displayed as Any, but exported as None.
    """

    def render(self, value):
        if not value:
            return "Any"

        return array_to_string(value)

    def value(self, value):
        if not value:
            return ""

        return array_to_string(value)


class ObjectAliasListColumn(tables.Column):
    """Display the Object Aliases with links but export them without."""

    def render(self, value):
        return object_list_to_string(value.all(), linkify=True)

    def value(self, value):
        return object_list_to_string(value.all(), linkify=False, separator=",")


class RuntimeTemplateColumn(columns.TemplateColumn):
    """Allow setting the extra_context at runtime instead of model instantiation."""

    attrs = {"td": {"class": "text-end text-nowrap noprint"}}

    def render(self, record, table, *args, **kwargs):
        if table.extra_context:
            self.extra_context.update(table.extra_context)
        return super().render(record, table, *args, **kwargs)
