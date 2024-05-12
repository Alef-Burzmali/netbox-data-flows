from netbox.plugins import PluginConfig

__version__ = "1.0.0"


class DataFlowsConfig(PluginConfig):
    name = "netbox_data_flows"
    verbose_name = "Data Flows"
    description = (
        "NetBox plugin to document data flows between "
        "systems and applications."
    )
    version = __version__
    base_url = "data-flows"
    author = "Thomas Fargeix"
    required_settings = []
    default_settings = {}
    min_version = "4.0.0"
    max_version = "4.0.99"

    def ready(self):
        from . import signals  # noqa: F401

        super().ready()


config = DataFlowsConfig
