from extras.plugins import PluginConfig

__version__ = "0.2.0"


class DataFlowsConfig(PluginConfig):
    name = "netbox_data_flows"
    verbose_name = "Data Flows"
    description = "NetBox plugin to document applications and data flows"
    version = __version__
    base_url = "data-flows"
    author = "Thomas Fargeix"
    required_settings = []
    default_settings = {}
    min_version = "3.3.0"


config = DataFlowsConfig
