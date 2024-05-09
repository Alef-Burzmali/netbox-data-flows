from netbox.plugins import PluginConfig

__version__ = "0.8.3"


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
    min_version = "3.7.0"
    max_version = "3.7.9"

    def ready(self):
        from . import signals  # noqa: F401

        super().ready()


config = DataFlowsConfig
