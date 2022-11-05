# netbox-data-flows

Plugin for [NetBox](https://docs.netbox.dev/) to document Data Flows between
systems and applications.

## WARNING

This plugin is considered Work in Progress. There are no guarantee on the
stability of the models and the availability of migrations for each updates.
YOU MAY LOOSE ALL YOUR DATA IF YOU USE THIS PLUGIN IN PRODUCTION!

## Dependencies
  - NetBox (>=3.3.0)

*Note:* the plugin uses some classes that are not explicitely exported in 
NetBox's plugin API, such as MPTT Tree-based models. Upward compatiblity is
not guaranteed.

## Installation

Add this line in your local_requirements.txt and run upgrade.sh:
```
netbox_data_flows @ https://github.com/Alef-Burzmali/netbox-data-flows/archive/refs/tags/vX.Y.Z.zip
```

## Data model

**Applications** are logical grouping of data flows and can be business
applications or infrastructure. Examples of applications:
  - Active Directory
  - MySuperBusinessApp
  - Network management
  - ...
  
Applications can be assigned an **Application Role**. An application role is a
label to help you categorize your applications. Examples of roles:
  - Infrastructure
  - Business Division 1
  - ...
  
Applications can be assigned one or more Services. This has no effect and will
be removed in a future version.
*WIP:* remove Services assigned to applications.

**Data Flows** modelize a network connection between two objects. A Data Flow
must be assigned to an application. Data Flows can be organized in hierarchical
trees to simplify their management. All Data Flows of the same tree must belong
to the same application.

Data Flows may or may not have a specification (source, destination, ports and
protocol). The specification of a parent has no effect on its children;
however, if a parent is disabled, all its descendants are implicitly disabled
too.

If a specification is given, it must have a protocol and at least a source or
a destination. Missing ports, sources or destinations are considered as "Any".
At most one source and one destination can be given.
Supported source and destination objects are:
  - Devices
  - Virtual Machines
  - Prefixes
  - IP Addresses

*WIP:* it is planned to introduce a new "Alias"/"Group" object to regroup
several objects in a single source or destination and to allow only Devices,
Virtual Machines, Prefixes and IP Ranges. Services / IP Addresses will be
allowed only if they belong to the Device or Virtual Machine.

**Data Flow Templates** are template of data flows with or without a
specification that are not assigned to any application. It is possible to
create a new Data Flow from a existing template. Templates are also organized
in trees. Children are not copied when a template is copied.

## Usage

Use the filter forms in the table views and the filterset of the API to list
the data flows with certain ports, sources or destinations, or the data flows
involving specific devices.

## Conversion to rules

Once your Data Flows are documented, use the "Data Flow Rules" view to see
all the enabled Data Flows with a specification in a flat view. This can be
used to create your firewall rules, for example.
*WIP:* regroup as much as possible similar rules.

