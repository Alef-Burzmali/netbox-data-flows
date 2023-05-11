from extras.plugins import PluginMenu, PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices


#
# Utility functions
#

APP_LABEL = "netbox_data_flows"


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
                color=ButtonColorChoices.GREEN,
            )
        )
    if "import" in actions:
        buttons.append(
            PluginMenuButton(
                link=f"plugins:{APP_LABEL}:{model_name}_import",
                title="Import",
                icon_class="mdi mdi-upload",
                permissions=[f"{APP_LABEL}.add_{model_name}"],
                color=ButtonColorChoices.CYAN,
            )
        )

    return buttons


#
# Nav menus
#

menu = PluginMenu(
    label="Data Flows",
    icon_class="mdi mdi-vector-polyline",
    groups=(
        (
            "Applications",
            (
                get_model_item("application", "Applications"),
                get_model_item("applicationrole", "Application Roles"),
            ),
        ),
        (
            "Data Flows",
            (
                get_model_item("dataflow", "Data Flows"),
                get_model_item("dataflowgroup", "Data Flow Groups"),
                get_model_item("objectalias", "Object Aliases"),
            ),
        ),
    ),
)
