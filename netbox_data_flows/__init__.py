from extras.plugins import PluginConfig

__version__ = "0.8.3-dev"


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
    min_version = "3.6.0"

    def ready(self):
        from . import signals  # noqa: F401

        super().ready()


config = DataFlowsConfig
