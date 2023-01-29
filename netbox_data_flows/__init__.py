from extras.plugins import PluginConfig

__version__ = "0.4.1"


class DataFlowsConfig(PluginConfig):
    name = "netbox_data_flows"
    verbose_name = "Data Flows"
    description = "NetBox plugin to document applications and data flows"
    version = __version__
    base_url = "data-flows"
    author = "Thomas Fargeix"
    required_settings = []
    default_settings = {}
    min_version = "3.4.2"


config = DataFlowsConfig
