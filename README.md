# netbox-data-flows

Plugin for [NetBox](https://docs.netbox.dev/) to document Data Flows between
systems and applications.

## WARNING

This plugin is considered Work in Progress (Beta).
Please use caution if using this plugin for production!

## Dependencies
  - NetBox (>=3.4.2)

*Note:* the plugin uses some classes that are not explicitely exported in 
NetBox's plugin API, such as MPTT Tree-based models. Upward compatiblity is
not guaranteed.

## Installation

Add this line in your local_requirements.txt and run upgrade.sh:
```
netbox_data_flows @ https://github.com/Alef-Burzmali/netbox-data-flows/releases/download/v0.4.0/netbox-data-flows-0.4.0.tar.gz
```

## Data model

**Applications** are logical grouping of data flows and can be business
applications or infrastructure. Examples of applications:
  - Active Directory
  - MySuperBusinessApp
  - Network management
  - ...
  
**Application Role** is a label to help you categorize your applications.
Each Application may have one Application Role.
Examples of roles:
  - Infrastructure
  - Business Division 1
  - ...

**Data Flows** modelize a network connection between two objects. They may be
assigned to an Application

Data Flows should have a source, a destination, a protocol, source ports and
destination ports. Only the protocol is mandatory. 

**Data Flow Groups** form a forest of groups. A tree can be assigned to a
single Application. Data Flow Groups can be enabled and disabled and inherit
the status of their parent. Disabled Data Flow Groups disable all the Data
Flows contained within.

**Object Aliases** are a group of references to other NetBox objects. Object
Aliases are used as sources and destinations of Data Flows and corresponds to
the groups or aliases used in firewall configuration. Internally, Object
Aliases contain Object Alias Targets, because Django cannot create ManyToMany
relationships to generic objects. Object Alias Targets are not exposed in the
interface and should be transparent for the user.

Object Aliases currently supports:
  - IP Addresses (ipam.ipaddress)
  - IP Ranges (ipam.iprange)
  - Prefixes (ipam.prefix)
If an IP Address is assigned to a device or virtual machine, that device is
also displayed.

## Know bugs and limitations
  - REST API and GraphQL API are not tested

## Planned Evolution
  - Include data's type/nature and link to data flows or at rest on devices

## Nomenclature

The name of Data Flows, Data Flow Groups and Object Aliases is not
constrained. You may wish to enforce your own validation rules in your
configuration, e.g.:

```
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

## Conversion to rules

Once your Data Flows are documented, use the "Data Flow Rules" view to see
all the enabled Data Flows in a flat view. This can be
used to create your firewall rules, for example.
*WIP:* regroup as much as possible similar rules.

