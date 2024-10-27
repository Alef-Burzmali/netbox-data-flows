import django_tables2 as tables

from netbox.tables import columns
from utilities.data import array_to_string

from netbox_data_flows.utils.helpers import object_list_to_string


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
