from extras.plugins import PluginConfig


class NetBoxDataFlowsConfig(PluginConfig):
    name = "netbox_data_flows"
    verbose_name = " NetBox Data Flows"
    description = "NetBox plugin to document applications and data flows"
    version = "0.1"
    base_url = "data-flows"
    author = "Thomas Fargeix"
    required_settings = []
    default_settings = {}
    min_version = "3.3.0"


config = NetBoxDataFlowsConfig
