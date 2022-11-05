from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices


menu_items = (
    PluginMenuItem(
        link="plugins:netbox_data_flows:application_list",
        link_text="Applications",
        permissions=["netbox_data_flows.view_application"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_data_flows:application_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_data_flows.add_application"],
            ),
            PluginMenuButton(
                link="plugins:netbox_data_flows:application_import",
                title="Import",
                icon_class="mdi mdi-upload",
                color=ButtonColorChoices.CYAN,
                permissions=["netbox_data_flows.add_application"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_data_flows:applicationrole_list",
        link_text="Application Roles",
        permissions=["netbox_data_flows.view_applicationrole"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_data_flows:applicationrole_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_data_flows.add_applicationrole"],
            ),
            PluginMenuButton(
                link="plugins:netbox_data_flows:applicationrole_import",
                title="Import",
                icon_class="mdi mdi-upload",
                color=ButtonColorChoices.CYAN,
                permissions=["netbox_data_flows.add_applicationrole"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_data_flows:dataflow_list",
        link_text="Data Flows",
        permissions=["netbox_data_flows.view_dataflow"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_data_flows:dataflow_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_data_flows.add_dataflow"],
            ),
            PluginMenuButton(
                link="plugins:netbox_data_flows:dataflow_import",
                title="Import",
                icon_class="mdi mdi-upload",
                color=ButtonColorChoices.CYAN,
                permissions=["netbox_data_flows.add_dataflow"],
            ),
        ),
    ),
    PluginMenuItem(
        link="plugins:netbox_data_flows:dataflowtemplate_list",
        link_text="Data Flow Templates",
        permissions=["netbox_data_flows.view_dataflowtemplate"],
        buttons=(
            PluginMenuButton(
                link="plugins:netbox_data_flows:dataflowtemplate_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN,
                permissions=["netbox_data_flows.add_dataflowtemplate"],
            ),
            PluginMenuButton(
                link="plugins:netbox_data_flows:dataflowtemplate_import",
                title="Import",
                icon_class="mdi mdi-upload",
                color=ButtonColorChoices.CYAN,
                permissions=["netbox_data_flows.add_dataflowtemplate"],
            ),
        ),
    ),
)
