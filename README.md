# netbox-data-flows

Plugin for [NetBox](https://github.com/netbox-community/netbox) to document
Data Flows between systems and applications.

## WARNING

This plugin is considered Work in Progress (Beta).
Please use caution if using this plugin for production!

## Features

* Document data flows between IP addresses, IP ranges and prefixes
* Document the application that requires these data flows
* WIP: Prepare the list of data flows to be injested as firewall rules

## Installation and Configuration

Full reference: [Using Plugins - NetBox Documentation](https://docs.netbox.dev/en/stable/plugins/)

### Requirements

* NetBox (>=3.4.2, <3.6.0)
* Python 3.8 or higher

*Note:* the plugin uses some classes that are not explicitely exported in 
NetBox's plugin API, such as MPTT Tree-based models. Upward compatiblity is
not guaranteed.

### Temporary installation

Install the Python package:
```bash
source /opt/netbox/venv/bin/activate
pip install netbox-data-flows
```

Add the plugin in NetBox configuration
```python
# Add in: /opt/netbox/netbox/netbox/configuration.py

PLUGINS = [
  'netbox_data_flows',
]
```

Create the database migrations:
```bash
source /opt/netbox/venv/bin/activate
/opt/netbox/netbox/manage.py migrate netbox_data_flows
```

The plugin will be removed at the next NetBox update.

### Permanent installation

Add the Python package to `local_requirements`:
```bash
echo netbox-data-flows >> /opt/netbox/local_requirements.txt 
```

Add the plugin in NetBox configuration
```python
# Add in: /opt/netbox/netbox/netbox/configuration.py

PLUGINS = [
  'netbox_data_flows',
]
```

Run the `upgrade.sh` script:
```bash
/opt/netbox/upgrade.sh
```

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

## Data model

### Application and Application Role

**Applications** are logical grouping of data flows and can be business
applications or infrastructure. Examples of applications:
* Active Directory
* MySuperBusinessApp
* Network management
* ...
  
**Application Role** is a label to help you categorize your applications.
Each Application may have one Application Role.
Examples of roles:
* Infrastructure
* Business Division 1
* ...

### Data Flow

**Data Flows** modelize a network connection between two objects. They may be
assigned to an Application

Data Flows should have a source, a destination, a protocol, source ports and
destination ports. Only the protocol is mandatory. 

**Data Flow Groups** form a forest of groups. A tree can be assigned to a
single Application. Data Flow Groups can be enabled and disabled and inherit
the status of their parent. Disabled Data Flow Groups disable all the Data
Flows contained within.

### Object Alias

**Object Aliases** are a group of references to other NetBox objects. Object
Aliases are used as sources and destinations of Data Flows and corresponds to
the groups or aliases used in firewall configuration. Internally, Object
Aliases contain Object Alias Targets, because Django cannot create ManyToMany
relationships to generic objects. Object Alias Targets are not exposed in the
interface and should be transparent for the user.

Object Aliases currently supports:
* IP Addresses (ipam.ipaddress)
* IP Ranges (ipam.iprange)
* Prefixes (ipam.prefix)
If an IP Address is assigned to a device or virtual machine, that device is
also displayed.

## Development

Contributions are welcomed. This plugin is developped on the free time of its
author, so do not expect regular releases.

### Know bugs and limitations
* REST API and GraphQL API are not tested

See also the [list of issues](https://github.com/Alef-Burzmali/netbox-data-flows/issues)

###  Planned Evolution
* Include data's type/nature and link to data flows or at rest on devices

