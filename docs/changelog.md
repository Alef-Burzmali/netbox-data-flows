# Changelog

The full changlelog for each release is available in the [release list](https://github.com/Alef-Burzmali/netbox-data-flows/releases).

## Versions v1.6 - 2026-09

Indirect and tagged matching for object alias membership, based on parent prefixes and ranges, or on device and virtual machine tags.

### Major changes

* Dropping support for NetBox 4.6.
* Indirect matching based on parent Prefix or IP Range when identifying applicable objet aliases.
* Device and virtual machine tags to match primary, oob or all assigned IP addresses to an object alias dynamically.

## Versions v1.5 - 2026-01

Activation of NetBox 4.5 features (including owners and better filterset).

### Major changes

* Adding support for NetBox 4.6 and 4.7, dropping support for NetBox 4.3, 4.4 and 4.5
* Owner and filterset from NetBox 4.5

## Versions v1.4 - 2025-09

Internal housekeeping.

### Major changes

* Adding support for NetBox 4.5, dropping support for NetBox 4.2

## Versions v1.3 - 2025-09

Addition of ICMP types.

### Major changes

* Adding support for NetBox 4.4
* Add ICMP types that can be added to data flows, when selecting ICMPv4 or ICMPv6 as the protocol.

## Versions v1.2 - 2025-08

Support for tenant and inherited tags for data flow groups and data flows.

### Major changes

* Adding support for NetBox 4.4, dropping support for NetBox 4.0 and 4.1
* Add tenants to applications, data flows and data flow groups.
* Add inherited tags from data flow groups to children groups and data flows (REST API only).

## Versions v1.1 - 2024-12

Internal rework with deletion of the ObjectAliasTarget internal object.

### Major changes

* Adding support for NetBox 4.2 and 4.3
* Removal of ObjectAliasTarget.

## Versions v1.0 - 2024-05

First stable release with support for NetBox v4.0.

### Major changes

* Support for NetBox 4.0 and 4.1
* Add a [documentation](https://github.com/Alef-Burzmali/netbox-data-flows/blob/main/docs/) and a [Quick Start guide](https://github.com/Alef-Burzmali/netbox-data-flows/blob/main/docs/quick-start.md).
* Add a test suite.
