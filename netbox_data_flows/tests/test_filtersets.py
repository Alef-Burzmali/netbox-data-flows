from django.test import TestCase

from dcim import models as dcim
from ipam import models as ipam
from virtualization import models as virtualization

from netbox_data_flows import choices, filtersets, models

from .data import TestData


class ApplicationRoleTestCase(TestCase):
    queryset = models.ApplicationRole.objects.all()
    filterset = filtersets.ApplicationRoleFilterSet

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        data.applicationroles

    def test_q(self):
        params = {"q": "FOObar 2"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"q": "APPLICATION ROLE"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"q": "application-role-1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {"name": ["Application Role 1", "Application Role 3"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {"slug": ["application-role-1", "application-role-3"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["foobar 2", "foobar 1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ApplicationTestCase(TestCase):
    queryset = models.Application.objects.all()
    filterset = filtersets.ApplicationFilterSet

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        data.applications

    def test_q(self):
        params = {"q": "application 2"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"q": "barFOO"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_name(self):
        params = {"name": ["Application 1", "Application 3"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["barfoo 2", "barfoo 1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_role(self):
        roles = models.ApplicationRole.objects.all()[:2]
        params = {"role_id": [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"role": [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)


class DataFlowGroupTestCase(TestCase):
    queryset = models.DataFlowGroup.objects.all()
    filterset = filtersets.DataFlowGroupFilterSet

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        data.dataflowgroups
        cls.tags = data.tags

    def test_q(self):
        params = {"q": "FOObar2"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"q": "GROUP 1.2"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"q": "GROUP-1-1-1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {"name": ["Group 1.1", "Group 3"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {"slug": ["group-1", "group-3"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["foobar2", "foobar1"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {"status": choices.DataFlowStatusChoices.STATUS_ENABLED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 7)
        params = {"status": choices.DataFlowStatusChoices.STATUS_DISABLED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_inherited_status(self):
        params = {"inherited_status": choices.DataFlowStatusChoices.STATUS_ENABLED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {"inherited_status": choices.DataFlowStatusChoices.STATUS_DISABLED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_inherited_tags(self):
        tags = self.tags
        params = {"inherited_tag": [tags[1]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {"inherited_tag": [tags[2]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"inherited_tag": [tags[0], tags[3]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"inherited_tag": [tags[0], tags[5]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_parent(self):
        groups = self.queryset.all()[:3]

        params = {"parent_id": [groups[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"parent_id": [groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"parent_id": [groups[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"parent_id": [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

        params = {"parent": [groups[0].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"parent": [groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"parent": [groups[2].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"parent": [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_ancestor(self):
        groups = self.queryset.all()[:3]

        params = {"ancestor_id": [groups[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {"ancestor_id": [groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"ancestor_id": [groups[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"ancestor_id": [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)

        params = {"ancestor": [groups[0].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)
        params = {"ancestor": [groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"ancestor": [groups[2].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"ancestor": [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 8)

    def test_application(self):
        applications = models.Application.objects.all()[:2]
        params = {"application_id": [applications[0].pk, applications[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"application": [applications[0].name, applications[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_application_role(self):
        roles = models.ApplicationRole.objects.all()[:2]
        params = {"application_role_id": [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {"application_role": [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)


class ObjectAliasTestCase(TestCase):
    queryset = models.ObjectAlias.objects.all()
    filterset = filtersets.ObjectAliasFilterSet

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        data.objectaliases

    def test_q(self):
        params = {"q": "OBJECT ALIAS 1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"q": "device"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {"name": ["Object Alias 1", "Object Alias 3"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["Device 1 and Device 2", "VM 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_prefixes(self):
        prefixes = ipam.Prefix.objects.all()
        params = {"prefixes": [prefixes[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"prefixes": [prefixes[0].pk, prefixes[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"prefixes": [prefixes[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_ip_ranges(self):
        ip_ranges = ipam.IPRange.objects.all()
        params = {"ip_ranges": [ip_ranges[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"ip_ranges": [ip_ranges[0].pk, ip_ranges[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"ip_ranges": [ip_ranges[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_ip_addresses(self):
        ip_addresses = ipam.IPAddress.objects.all()
        params = {"ip_addresses": [ip_addresses[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"ip_addresses": [ip_addresses[0].pk, ip_addresses[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"ip_addresses": [ip_addresses[4].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_devices(self):
        devices = dcim.Device.objects.all()
        params = {"devices": [devices[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"devices": [devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"devices": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_machines(self):
        virtual_machines = virtualization.VirtualMachine.objects.all()
        params = {"virtual_machines": [virtual_machines[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {
            "virtual_machines": [
                virtual_machines[0].pk,
                virtual_machines[1].pk,
            ]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_multiple_targets(self):
        params = {
            "prefixes": [ipam.Prefix.objects.first().pk],
            "ip_ranges": [ipam.IPRange.objects.first().pk],
            "ip_addresses": [ipam.IPAddress.objects.first().pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {
            "devices": [dcim.Device.objects.first().pk],
            "virtual_machines": [virtualization.VirtualMachine.objects.first().pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {
            "ip_addresses": [ipam.IPAddress.objects.first().pk],
            "virtual_machines": [virtualization.VirtualMachine.objects.first().pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {
            "ip_addresses": [ipam.IPAddress.objects.first().pk],
            "devices": [dcim.Device.objects.first().pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DataFlowTestCase(TestCase):
    queryset = models.DataFlow.objects.all()
    filterset = filtersets.DataFlowFilterSet

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        data.dataflows
        cls.tags = data.tags

    def test_q(self):
        params = {"q": "DATA FLOW 1"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"q": "udp"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {"name": ["Data Flow 1", "Data Flow 3"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["ICMPv4 Echo Request and Echo Reply from any to any"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_status(self):
        params = {"status": choices.DataFlowStatusChoices.STATUS_ENABLED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {"status": choices.DataFlowStatusChoices.STATUS_DISABLED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_inherited_status(self):
        params = {"inherited_status": choices.DataFlowStatusChoices.STATUS_ENABLED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {"inherited_status": choices.DataFlowStatusChoices.STATUS_DISABLED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_inherited_tags(self):
        tags = self.tags
        params = {"inherited_tag": [tags[1]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {"inherited_tag": [tags[2]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"inherited_tag": [tags[0], tags[3]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"inherited_tag": [tags[0], tags[5]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"inherited_tag": [tags[6]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_application(self):
        applications = models.Application.objects.all()[:2]
        params = {"application_id": [applications[0].pk, applications[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"application": [applications[0].name, applications[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_application_role(self):
        roles = models.ApplicationRole.objects.all()[:2]
        params = {"application_role_id": [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"application_role": [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_group(self):
        groups = models.DataFlowGroup.objects.all()
        params = {"group_id": [groups[2].pk, groups[3].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"group": [groups[2].slug, groups[3].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"group_id": [groups[6].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"group": [groups[6].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_recursive_group(self):
        groups = models.DataFlowGroup.objects.all()
        params = {"recursive_group_id": [groups[0].pk]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            5,
            f"Recursive group by ID: {groups[0]}",
        )
        params = {"recursive_group": [groups[0].slug]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            5,
            f"Recursive group by slug: {groups[0]}",
        )
        params = {"recursive_group_id": [groups[1].pk]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            1,
            f"Recursive group by ID: {groups[1]}",
        )
        params = {"recursive_group": [groups[1].slug]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            1,
            f"Recursive group by slug: {groups[1]}",
        )
        params = {"recursive_group_id": [groups[6].pk]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            4,
            f"Recursive group by ID: {groups[6]}",
        )
        params = {"recursive_group": [groups[6].slug]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            4,
            f"Recursive group by slug: {groups[6]}",
        )
        params = {"recursive_group_id": [groups[1].pk, groups[5].pk]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            5,
            f"Recursive group by ID: {groups[1]} and {groups[5]}",
        )
        params = {"recursive_group": [groups[1].slug, groups[5].slug]}
        self.assertEqual(
            self.filterset(params, self.queryset).qs.count(),
            5,
            f"Recursive group by slug: {groups[1]} and {groups[5]}",
        )

    def test_protocol(self):
        params = {"protocol": [choices.DataFlowProtocolChoices.PROTOCOL_ANY]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {
            "protocol": [
                choices.DataFlowProtocolChoices.PROTOCOL_ICMPv4,
                choices.DataFlowProtocolChoices.PROTOCOL_SCTP,
            ]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_source_ports(self):
        params = {"source_ports": [200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_ports": [55, 57]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_ports": [55, 57, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_destination_ports(self):
        params = {"destination_ports": [80]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_ports": [81]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"destination_ports": [81, 82]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"destination_ports": [81, 82, 300]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_source_and_destination_ports(self):
        params = {"source_ports": [55], "destination_ports": [81]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_ports": [55, 57], "destination_ports": [81, 82]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_ports": [200], "destination_ports": [200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_ports": [200], "destination_ports": [300]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"source_ports": [55, 57, 300], "destination_ports": [82]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_is_null(self):
        params = {"source_is_null": choices.TargetIsEmptyChoice.STATUS_NULL}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"source_is_null": choices.TargetIsEmptyChoice.STATUS_NOT_NULL}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_source_aliases(self):
        aliases = models.ObjectAlias.objects.all()
        params = {"source_aliases": [aliases[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {
            "source_aliases": [
                aliases[1].pk,
                aliases[3].pk,
                aliases[4].pk,
                aliases[6].pk,
            ]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"source_aliases": [aliases[1].pk, aliases[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_prefixes(self):
        prefixes = ipam.Prefix.objects.all()
        params = {"source_prefixes": [prefixes[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"source_prefixes": [prefixes[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_source_ip_ranges(self):
        ip_ranges = ipam.IPRange.objects.all()
        params = {"source_ip_ranges": [ip_ranges[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_ip_ranges": [ip_ranges[0].pk, ip_ranges[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_ip_addresses(self):
        ip_addresses = ipam.IPAddress.objects.all()
        params = {"source_ip_addresses": [ip_addresses[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_ip_addresses": [ip_addresses[0].pk, ip_addresses[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_ip_addresses": [ip_addresses[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_source_devices(self):
        devices = dcim.Device.objects.all()[:2]
        params = {"source_devices": [devices[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_devices": [devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_devices": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_source_virtual_machines(self):
        vms = virtualization.VirtualMachine.objects.all()[:2]
        params = {"source_virtual_machines": [vms[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"source_virtual_machines": [vms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"source_virtual_machines": [vms[0].pk, vms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_OR_of_sources(self):
        aliases = models.ObjectAlias.objects.all()[:1]
        prefixes = ipam.Prefix.objects.all()[:1]
        ip_ranges = ipam.IPRange.objects.all()[:1]
        ip_addresses = ipam.IPAddress.objects.all()[:3]
        devices = dcim.Device.objects.all()[:2]
        vms = virtualization.VirtualMachine.objects.all()[:2]

        params = {
            "source_is_null": choices.TargetIsEmptyChoice.STATUS_NULL,
            "source_aliases": [aliases[0].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {
            "source_prefixes": [prefixes[0].pk],
            "source_devices": [devices[0].pk, devices[1].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {
            "source_ip_ranges": [ip_ranges[0].pk],
            "source_ip_addresses": [ip_addresses[0].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {
            "source_devices": [devices[0].pk],
            "source_ip_addresses": [ip_addresses[0].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {
            "source_virtual_machines": [vms[1].pk],
            "source_devices": [devices[0].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_destination_is_null(self):
        params = {"destination_is_null": choices.TargetIsEmptyChoice.STATUS_NULL}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"destination_is_null": choices.TargetIsEmptyChoice.STATUS_NOT_NULL}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_destination_aliases(self):
        aliases = models.ObjectAlias.objects.all()
        params = {"destination_aliases": [aliases[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {
            "destination_aliases": [
                aliases[1].pk,
                aliases[3].pk,
                aliases[4].pk,
                aliases[6].pk,
            ]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"destination_aliases": [aliases[0].pk, aliases[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_destination_prefixes(self):
        prefixes = ipam.Prefix.objects.all()
        params = {"destination_prefixes": [prefixes[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_prefixes": [prefixes[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_destination_ip_ranges(self):
        ip_ranges = ipam.IPRange.objects.all()
        params = {"destination_ip_ranges": [ip_ranges[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_ip_ranges": [ip_ranges[0].pk, ip_ranges[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_destination_ip_addresses(self):
        ip_addresses = ipam.IPAddress.objects.all()
        params = {"destination_ip_addresses": [ip_addresses[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"destination_ip_addresses": [ip_addresses[0].pk, ip_addresses[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"destination_ip_addresses": [ip_addresses[5].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_destination_devices(self):
        devices = dcim.Device.objects.all()[:2]
        params = {"destination_devices": [devices[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"destination_devices": [devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_devices": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_destination_virtual_machines(self):
        vms = virtualization.VirtualMachine.objects.all()[:2]
        params = {"destination_virtual_machines": [vms[0].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"destination_virtual_machines": [vms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"destination_virtual_machines": [vms[0].pk, vms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_OR_of_destinations(self):
        aliases = models.ObjectAlias.objects.all()[:2]
        prefixes = ipam.Prefix.objects.all()[:1]
        ip_ranges = ipam.IPRange.objects.all()[:1]
        ip_addresses = ipam.IPAddress.objects.all()[:3]
        devices = dcim.Device.objects.all()[:2]
        vms = virtualization.VirtualMachine.objects.all()[:2]

        params = {
            "destination_is_null": choices.TargetIsEmptyChoice.STATUS_NULL,
            "destination_aliases": [aliases[1].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {
            "destination_prefixes": [prefixes[0].pk],
            "destination_devices": [devices[0].pk, devices[1].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {
            "destination_ip_ranges": [ip_ranges[0].pk],
            "destination_ip_addresses": [ip_addresses[0].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {
            "destination_devices": [devices[0].pk],
            "destination_ip_addresses": [ip_addresses[0].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {
            "destination_virtual_machines": [vms[1].pk],
            "destination_devices": [devices[0].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_AND_of_source_and_destinations(self):
        aliases = models.ObjectAlias.objects.all()
        prefixes = ipam.Prefix.objects.all()[:1]
        devices = dcim.Device.objects.all()[:2]
        vms = virtualization.VirtualMachine.objects.all()[:2]

        params = {
            "source_is_null": choices.TargetIsEmptyChoice.STATUS_NULL,
            "destination_is_null": choices.TargetIsEmptyChoice.STATUS_NULL,
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {
            "source_is_null": choices.TargetIsEmptyChoice.STATUS_NOT_NULL,
            "destination_is_null": choices.TargetIsEmptyChoice.STATUS_NULL,
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {
            "source_is_null": choices.TargetIsEmptyChoice.STATUS_NULL,
            "destination_is_null": choices.TargetIsEmptyChoice.STATUS_NOT_NULL,
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {
            "source_is_null": choices.TargetIsEmptyChoice.STATUS_NOT_NULL,
            "destination_is_null": choices.TargetIsEmptyChoice.STATUS_NOT_NULL,
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

        params = {
            "source_is_null": choices.TargetIsEmptyChoice.STATUS_NULL,
            "destination_aliases": [aliases[3].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {
            "source_devices": [devices[1].pk],
            "destination_is_null": choices.TargetIsEmptyChoice.STATUS_NULL,
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {
            "source_prefixes": [prefixes[0].pk],
            "destination_virtual_machines": [vms[0].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

        params = {
            "source_devices": [devices[0].pk],
            "destination_devices": [devices[0].pk],
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
