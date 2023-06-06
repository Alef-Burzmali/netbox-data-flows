from netbox.tables import columns


class RuntimeTemplateColumn(columns.TemplateColumn):
    """
    Allow setting the extra_context at runtime instead of model instantiation
    """

    attrs = {"td": {"class": "text-end text-nowrap noprint"}}

    def render(self, record, table, *args, **kwargs):
        if table.extra_context:
            self.extra_context.update(table.extra_context)
        return super().render(record, table, *args, **kwargs)
