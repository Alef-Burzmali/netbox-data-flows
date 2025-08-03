from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem
from netbox.plugins.utils import get_plugin_config


#
# Utility functions
#

APP_LABEL = "netbox_data_flows"
top_level_menu = get_plugin_config("netbox_data_flows", "top_level_menu")


# clone of netbox.navigation_menu.get_model_item, but for plugin
def get_model_item(model_name, label, actions=("add", "import")):
    return PluginMenuItem(
        link=f"plugins:{APP_LABEL}:{model_name}_list",
        link_text=label,
        permissions=[f"{APP_LABEL}.view_{model_name}"],
        buttons=get_model_buttons(model_name, actions),
    )


# clone of netbox.navigation_menu.get_model_buttons, but for plugin
def get_model_buttons(model_name, actions=("add", "import")):
    buttons = []

    if "add" in actions:
        buttons.append(
            PluginMenuButton(
                link=f"plugins:{APP_LABEL}:{model_name}_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                permissions=[f"{APP_LABEL}.add_{model_name}"],
            )
        )
    if "import" in actions:
        buttons.append(
            PluginMenuButton(
                link=f"plugins:{APP_LABEL}:{model_name}_bulk_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=[f"{APP_LABEL}.add_{model_name}"],
            )
        )

    return buttons


#
# Nav menus
#

application_item = get_model_item("application", "Applications")
applicationrole_item = get_model_item("applicationrole", "Application Roles")
dataflow_item = get_model_item("dataflow", "Data Flows")
dataflowgroup_item = get_model_item("dataflowgroup", "Data Flow Groups")
objectalias_item = get_model_item("objectalias", "Object Aliases")

if top_level_menu:
    menu = PluginMenu(
        label="Data Flows",
        icon_class="mdi mdi-vector-polyline",
        groups=(
            (
                "Applications",
                (
                    application_item,
                    applicationrole_item,
                ),
            ),
            (
                "Data Flows",
                (
                    dataflow_item,
                    dataflowgroup_item,
                    objectalias_item,
                ),
            ),
        ),
    )
else:
    menu_items = [
        application_item,
        applicationrole_item,
        dataflow_item,
        dataflowgroup_item,
        objectalias_item,
    ]
