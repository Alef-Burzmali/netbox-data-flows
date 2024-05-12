# Data Model and Design's Decisions

If you want an example on how to use the plugin, head towards the [quick start tutorial](quick-start.md).

## Plugin's objectives

The goal of this plugin is to document the data flows of applications and systems, which should already be documented in your NetBox instance.

It aims to:
* Document known TCP, UDP, ICMP or SCTP data flows
* Group them and link them to applications for better manageability
* Provide a useful source of truth to generate firewall or other filtering rules (network ACL, security contracts, etc.)

It does not try to:
* Document the existing firewall or network filtering rules
* Provision firewall or filtering rules (still possible via scripts)

## Design considerations

The plugin tries to use the native NetBox objects when relevant. However, data flows are not directly between physical devices or virtual machines, instead they sit at a higher application level and are relatively agnostic of the physical world under them.

Furthermore, a device may have several network interfaces, each with zero, one or several IP addresses. An application may be configured to use a specific IP address to sent a data flow from, or to listen on or it can use any available IP address and let the operating system figure which one is used.

For some data flows, it does not make sense to specify single IP addresses as source or as destination. For example, all the devices in a network segment may want to connect to the same DNS or LDAP servers. Or a monitoring server may scan entire network ranges.

As such, it was decided to use NetBox's **IP Address**, **IP Range** and **IP Prefix** objects as the sources and destinations of data flows:
* If the source is a single IP of a single device, you can use the IP Address assigned to that device.
* If the source is any IP of a device, you can list all the IP addresses assigned to that device.
* If the destination is a whole Prefix or IP Range, you can use that object.
* If the destination is a specific set of IP Addresses, you can list them explicitely.

It was decided not to use the native **Service** object:
* The Service represents a TCP, SCTP or UDP listener and does not work as a possible Source for the data flow
* It does not support other protocols, such as ICMP
* It is easy to combine a list of IP, prefixes and ranges, but combining them with a service (i.e.: a IP/protocol/port association) is much more complicated 
* Trying to bypass these limitations led to a technical implementation that was too complex and error-prone.

To ease maintenance, the IP Addresses, IP Ranges and Prefixes are grouped in Object Aliases. These can be seen as reusable groups of addresses that can be a source or a destination to one or several data flows.


## Plugin limitations

The plugin cannot modify the native NetBox objects and add ForeignKey relations. However, it requires a Many to Many relationship between the Object Aliases (or the source/destination) and different types of objects (IP Address, IP Range and Prefix) and Generic Many to Many relationships are not supported by Django (nor a good idea in general).

To circumvent this limitation, the plugin makes use of a proxy object, Object Alias Target, that represents one-to-one a NetBox's native IP Address, IP Range or Prefix. These proxy objects are automatically created when needed and destroyed when the linked object is deleted, and the user should not have to worry about them. However, some usecases (like creating object aliases via the API) may need to be aware of them.


## Data Model

The following sections explain the different objects created by the plugin.

![Data model of NetBox Data Flows](media/data-model.png)

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

**Data Flows** modelize a network connection between two objects. They may be assigned to an Application.

Data Flows should have a source, a destination, a protocol, source ports and destination ports. Only the protocol is mandatory. 

**Data Flow Groups** form a forest of groups. They can also be assigned to an Application. Data Flow Groups can be enabled and disabled and inherit the status of their parent. Disabled Data Flow Groups disable all the Data Flows contained within.

### Object Alias

**Object Aliases** are a group of references to other NetBox objects. Object Aliases are used as sources and destinations of Data Flows and corresponds to the groups or aliases used in firewall configuration.

Internally, Object Aliases contain **Object Alias Targets**, because Django cannot create ManyToMany relationships to generic objects. Object Alias Targets are not exposed in the interface and should be transparent for the user.

Object Aliases can contain:
* IP Addresses (ipam.ipaddress)
* IP Ranges (ipam.iprange)
* Prefixes (ipam.prefix)
If an IP Address is assigned to a device or virtual machine, that device is
also displayed.
