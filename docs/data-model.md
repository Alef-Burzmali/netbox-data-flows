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


## Data Model

The following sections explain the different objects created by the plugin.

![Data model of NetBox Data Flows](media/data-model.png)

### Application and Application Role

**Applications** are logical grouping of data flows and can be business
applications or infrastructure.

Examples of applications:

* Active Directory
* MySuperBusinessApp
* Network management
* ...

You can optionally use a custom field to assign your devices and other object to specific applications.
See the Options section of [the configuration guide](installation-configuration.md#options)

**Application Role** is a label to help you categorize your applications.
Each Application may have one Application Role.

Examples of roles:

* Infrastructure
* Business Division 1
* ...

### Data Flow

**Data Flows** modelize a network connection between two objects. They may be assigned to an Application.

Data Flows should have a source, a destination, a protocol, source ports and destination ports. Only the protocol is mandatory.

By convention, if the list of source ports or destination ports is empty, this means "Any" port is accepted (for transport protocols with ports). The interface will display `Any`. API and exports will return an empty list.

**Data Flow Groups** form a forest of groups. They can also be assigned to an Application. Data Flow Groups can be enabled and disabled and inherit the status of their parent. Disabled Data Flow Groups disable all the Data Flows contained within.

Only in the REST API, the inherited list of tags is available (inherited_tags when reading and inherited_tag when filtering). This is the set of tags of the data flow and its parent groups. This field is not displyed in the UI.

### Object Alias

**Object Aliases** are a group of references to other NetBox objects. Object Aliases are used as sources and destinations of Data Flows and corresponds to the groups or aliases used in firewall configuration.

Object Aliases can contain any number of static members:

* IP Addresses (`ipam.ipaddress`)
* IP Ranges (`ipam.iprange`)
* Prefixes (`ipam.prefix`)

Object Aliases can also include dynamic members by selecting tags for:

* Devices (`dcim.device`)
* Virtual Machines (`virtualization.virtualmachine`)

Three tag matching rules are available:

* Primary IP only (default): only the primary IPv4 and IPv6 of the device or virtual machine are matched.
* OOB IP only: only the out-of-band IP of the device is matched (VM have no OOB IP).
* All IPs: any IP address assigned to any interface of the device or virtual machine are matched.

The machine tags, IP matching rule and optional interface tags are separate selectors:

| Field | Values / default | Meaning |
| --- | --- | --- |
| `machine_tag_operator` | `any` (default), `all` | Match at least one or every selected tag on the same machine. Applied separately to `device_tags` and `virtual_machine_tags`. |
| `interface_tags` | Tags; empty by default | Restrict dynamic IPs to interfaces of the selected machines carrying these tags. |
| `interface_tag_operator` | `any` (default), `all` | Match at least one or every selected tag on the same interface, independently of the machine operator. |

A machine selector with no tags selects no machines of that type. Device and virtual machine results are combined. Interface tags alone do not select machines globally. The alias's own `tags` field remains metadata, separate from these selectors.

Interface tags further restrict the IP matching rule: `primary` or `oob` addresses must also be assigned to a matching interface. `all` means all assigned IPs **after** applying the interface filter; it does not mean all tags must match. The `oob` rule uses the device's NetBox OOB IP field, not an interface tag named OOB. VMs can use interfaces tagged OOB with the `all` rule.

All tags must match on a single object when using the `all` operator. Tags on different machines or interfaces cannot satisfy a selector together. Only directly assigned IPs are included; parent or child interfaces do not inherit tag selection. Multiple IPv4 and IPv6 addresses on a selected interface are included according to the IP matching rule. Interface and IP statuses are not implicitly filtered.

An empty interface selector preserves the existing IP matching behavior. A nonempty selector with no matching interface or address contributes no dynamic IPs, without falling back to another interface. Static members remain included independently of all tag selectors. Duplicate IP objects are returned once. Resolution uses the current tags and IP assignments, without copying dynamic IPs into static membership.

The REST API accepts tag IDs for all selector lists. For example, if ALPHA, BETA and OOB have IDs 101, 102 and 201:

```json
{
  "name": "example_oob",
  "virtual_machine_tags": [101, 102],
  "machine_tag_operator": "all",
  "tag_matching_rule": "all",
  "interface_tags": [201],
  "interface_tag_operator": "any"
}
```

This selects the OOB-tagged interfaces of VMs carrying both ALPHA and BETA. Additional interface tags with `interface_tag_operator=any` select alternative interfaces, while `all` requires every tag on the same interface.

Omitted fields in a REST PATCH retain their values; `interface_tags: []` removes the interface filter. Both operators default to `any`, preserving existing aliases. Operators are also optional CSV columns; dynamic tag lists are managed through the UI or REST API. In bulk editing, use the interface tag clear option to remove that selector.

The REST API exposes the selectors and static members. Its `ip_addresses` field contains only static IP members; dynamic IPs are displayed in the alias details and data flow Targets tab.

There is no defined meaning for an empty object alias, but it can be used when:
* The aliased object is not documented in NetBox (e.g.: third party public IP addresses)
* The alias is "Any" / "Internet" destination

When filtering object aliases or displaying them in a device or virtual machine's data flow tab, you have three matching types:

* Direct: are the prefixes, IP ranges and IP addresses explicitly added to an object alias.
* Indirect: are prefixes, IP ranges or IP addresses that are fully within another prefix or IP range which are added to the object alias.
* Tagged: are the IP addresses selected dynamically by the machine tags, IP matching rule and optional interface tags described above.
