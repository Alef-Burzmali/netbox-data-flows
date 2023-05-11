from extras.plugins import PluginConfig

__version__ = "0.5.1.post1"


class DataFlowsConfig(PluginConfig):
    name = "netbox_data_flows"
    verbose_name = "Data Flows"
    description = "NetBox plugin to document data flows between systems and applications."
    version = __version__
    base_url = "data-flows"
    author = "Thomas Fargeix"
    required_settings = []
    default_settings = {}
    min_version = "3.4.2"
    max_version = "3.5.99"

    def ready(self):
        from . import signals

        super().ready()


config = DataFlowsConfig
