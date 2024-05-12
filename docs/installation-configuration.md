# Installation and Configuration

## How to install

NetBox Data Flows is a [NetBox](https://github.com/netbox-community/netbox) plugin.

Full reference: [Using Plugins - NetBox Documentation](https://docs.netbox.dev/en/stable/plugins/).

Once installed, go to the [quick start guide](quick-start.md) to discover how to use the plugin.

### Supported Versions

| netbox version | netbox-data-flows version     |
| -------------- | ----------------------------- |
| >= 4.0.0       | >= v0.9.0                     |
| >= 3.7.0       | >= v0.8.0                     |
| >= 3.6.0       | >= v0.7.3                     |
|  < 3.6.0       | Not supported                 |

> [!CAUTION]
> Plugin versions before v0.7.3 can support earlier versions of NetBox. However, they are buggy and not recommended for production use.

> [!WARNING]
> The plugin uses some classes that are not explicitely exported in 
NetBox's plugin API, such as MPTT Tree-based models. Upward compatiblity is 
not fully guaranteed.

### Dependencies

* NetBox (>=4.0.0)
* Python 3.10 or higher

### Installation

The plugin is available at [PyPi](https://pypi.org/project/netbox-data-flows/).

Add the Python package to your `local_requirements` file:
```bash
echo netbox-data-flows >> /opt/netbox/local_requirements.txt 
```

Enable the plugin in NetBox configuration:
```python
# Add in: /opt/netbox/netbox/netbox/configuration.py

PLUGINS = [
  'netbox_data_flows',
]
```

Run NetBox's `upgrade.sh` script to download the plugin and run the migrations:
```bash
/opt/netbox/upgrade.sh
```

### Upgrade

The latest version from PyPi is always installed when `upgrade.sh` is run again, thus the plugin will be updated when you update your NetBox instance.

You can manually update the plugin without upgrading NetBox with:
```bash
# Enter NetBox venv
. /opt/netbox/venv/bin/activate

# Update the plugin
pip install --upgrade netbox-data-flows

# Run the migrations
/opt/netbox/netbox/manage.py migrate netbox_data_flows

# Restart the NetBox server
systemctl restart netbox.service netbox-rq.service
```

### Uninstallation

Disable the plugin in NetBox configuration: remove `netbox_data_flows` from `PLUGINS`.

Remove `netbox-data-flows` from your `local_requirements` file. You can run `upgrade.sh` or enter the venv and use `pip` to uninstall `netbox-data-flows`.

Deleting the data of the plugin is not recommended. If you really want to do it:

* Enable the venv and launch NetBox's dbshell
* Drop all the `netbox_data_flows_*` tables, e.g.:
  `DROP TABLE netbox_data_flows_applicationrole CASCADE`)
* Delete the migrations of the plugin:
  `DELETE FROM "django_migrations" where "app" = 'netbox_data_flows';`


## Configuration

There is no `PLUGIN_CONFIG` configuration for this plugin. However, several
other aspects can be configured.

### Nomenclature

The name of Data Flows, Data Flow Groups and Object Aliases is not
constrained. You may wish to enforce your own validation rules in your
configuration, e.g.:

```python
# Add in: /opt/netbox/netbox/netbox/configuration.py

CUSTOM_VALIDATORS = {
    "netbox_data_flows.objectalias": [
        {
            "name": {
                "regex": "(host|net)_[a-z_]+"
            },
        }
    ]
}
```

Similar settings can be applied to:
* Applications: netbox_data_flows.application
* Application Roles: netbox_data_flows.applicationrole
* Data Flows: netbox_data_flows.dataflow
* Data Flow Groups: netbox_data_flows.dataflowgroup
* Object Aliases: netbox_data_flows.objectalias

Full reference: [CUSTOM_VALIDATORS - NetBox Documentation](https://docs.netbox.dev/en/stable/configuration/data-validation/#custom_validators)

### Protocol Choices

You can edit the list of available protocols when creating a data flow.

```python
# Add in: /opt/netbox/netbox/netbox/configuration.py

FIELD_CHOICES = {
    'netbox_data_flows.DataFlow.protocol+': (
        ('igmp', "IGMP"),
    )
}
```

Full reference: [FIELD_CHOICES - NetBox Documentation](https://docs.netbox.dev/en/stable/configuration/data-validation/#field_choices)