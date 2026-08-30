import random

from django.db.models import QuerySet
from django.test import TestCase

from utilities.testing import create_tags

from dcim import models as dcim
from ipam import models as ipam
from virtualization import models as virtualization

from netbox_data_flows import choices, models

from .data import TestData


class ObjectAliasTestCase(TestCase):
    model = models.ObjectAlias

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        data.objectaliases

    def test_qs_contains_empty(self):
        qs = self.model.objects.contains()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 0)

    def test_qs_contains_direct(self):
        aliases = models.ObjectAlias.objects.all()

        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.contains(*ips, direct=True)
        self.assertIn(aliases[3], qs)
        self.assertIn(aliases[4], qs)
        self.assertEqual(qs.count(), 2)

        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.contains(*iprange, direct=True)
        self.assertIn(aliases[2], qs)
        self.assertEqual(qs.count(), 1)

        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.contains(*pref, direct=True)
        self.assertIn(aliases[0], qs)
        self.assertIn(aliases[2], qs)
        self.assertEqual(qs.count(), 2)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.contains(*dev, direct=True)
        self.assertIn(aliases[3], qs)
        self.assertIn(aliases[4], qs)
        self.assertEqual(qs.count(), 2)

        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.contains(*vm, direct=True)
        self.assertEqual(qs.count(), 2)
        self.assertIn(aliases[3], qs)
        self.assertIn(aliases[5], qs)
        self.assertEqual(qs.count(), 2)

        qs = self.model.objects.contains(pref[0], *vm, direct=True)
        self.assertEqual(qs.count(), 4)
        self.assertIn(aliases[0], qs)
        self.assertIn(aliases[2], qs)
        self.assertIn(aliases[3], qs)
        self.assertIn(aliases[5], qs)

    def test_qs_contains_indirect(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.contains(*ips, indirect=True)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 2)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.contains(*iprange, indirect=True)
        self.assertEqual(qs.count(), 2)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.contains(*pref, indirect=True)
        self.assertEqual(qs.count(), 2)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.contains(*dev, indirect=True)
        self.assertEqual(qs.count(), 2)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.contains(*vm, indirect=True)
        self.assertEqual(qs.count(), 2)

        qs = self.model.objects.contains(pref[0], *vm, indirect=True)
        self.assertEqual(qs.count(), 2)

    def test_get_resolved_ip_addresses_all_addresses(self):
        device_tag, virtual_machine_tag = create_tags("dynamic-device", "dynamic-virtual-machine")
        device = dcim.Device.objects.get(name="Device 1")
        virtual_machine = virtualization.VirtualMachine.objects.get(name="VM 2")
        device.tags.add(device_tag)
        virtual_machine.tags.add(virtual_machine_tag)

        direct_ip = ipam.IPAddress.objects.get(address="10.10.0.1/24")

        alias = self.model.objects.create(
            name="Object Alias Dynamic",
            description="Dynamic targets",
            tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_ALL,
        )
        alias.ip_addresses.set([direct_ip])
        alias.device_tags.set([device_tag])
        alias.virtual_machine_tags.set([virtual_machine_tag])

        self.assertEqual(
            {str(address) for address in alias.get_resolved_ip_addresses().values_list("address", flat=True)},
            {
                "10.0.1.1/24",
                "10.0.1.2/24",
                "10.100.1.1/24",
                "10.10.0.1/24",
            },
        )
        self.assertEqual(
            {
                str(address)
                for address in alias.get_resolved_ip_addresses(include_direct_assignments=False).values_list(
                    "address",
                    flat=True,
                )
            },
            {
                "10.0.1.1/24",
                "10.0.1.2/24",
                "10.100.1.1/24",
            },
        )

    def test_get_resolved_ip_addresses_primary_addresses(self):
        device_tag, virtual_machine_tag = create_tags("dynamic-device", "dynamic-virtual-machine")
        device = dcim.Device.objects.get(name="Device 1")
        virtual_machine = virtualization.VirtualMachine.objects.get(name="VM 2")
        device.tags.add(device_tag)
        virtual_machine.tags.add(virtual_machine_tag)

        direct_ip = ipam.IPAddress.objects.get(address="10.10.0.1/24")

        device.primary_ip4 = device.interfaces.first().ip_addresses.first()
        device.save()
        virtual_machine.primary_ip4 = virtual_machine.interfaces.first().ip_addresses.first()
        virtual_machine.save()

        alias = self.model.objects.create(
            name="Object Alias Dynamic",
            description="Dynamic targets",
            tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_PRIMARY,
        )
        alias.ip_addresses.set([direct_ip])
        alias.device_tags.set([device_tag])
        alias.virtual_machine_tags.set([virtual_machine_tag])

        self.assertEqual(
            {str(address) for address in alias.get_resolved_ip_addresses().values_list("address", flat=True)},
            {
                "10.0.1.1/24",
                "10.100.1.1/24",
                "10.10.0.1/24",
            },
        )
        self.assertEqual(
            {
                str(address)
                for address in alias.get_resolved_ip_addresses(include_direct_assignments=False).values_list(
                    "address",
                    flat=True,
                )
            },
            {
                "10.0.1.1/24",
                "10.100.1.1/24",
            },
        )

    def test_get_resolved_ip_addresses_oob_addresses(self):
        device_tag, virtual_machine_tag = create_tags("dynamic-device", "dynamic-virtual-machine")
        device = dcim.Device.objects.get(name="Device 1")
        virtual_machine = virtualization.VirtualMachine.objects.get(name="VM 2")
        device.tags.add(device_tag)
        virtual_machine.tags.add(virtual_machine_tag)

        direct_ip = ipam.IPAddress.objects.get(address="10.10.0.1/24")

        device.oob_ip = device.interfaces.first().ip_addresses.first()
        device.save()
        virtual_machine.primary_ip4 = virtual_machine.interfaces.first().ip_addresses.first()
        virtual_machine.save()

        alias = self.model.objects.create(
            name="Object Alias Dynamic",
            description="Dynamic targets",
            tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_OOB,
        )
        alias.ip_addresses.set([direct_ip])
        alias.device_tags.set([device_tag])
        alias.virtual_machine_tags.set([virtual_machine_tag])

        self.assertEqual(
            {str(address) for address in alias.get_resolved_ip_addresses().values_list("address", flat=True)},
            {
                "10.0.1.1/24",
                "10.10.0.1/24",
            },
        )
        self.assertEqual(
            {
                str(address)
                for address in alias.get_resolved_ip_addresses(include_direct_assignments=False).values_list(
                    "address",
                    flat=True,
                )
            },
            {
                "10.0.1.1/24",
            },
        )

    def test_get_resolved_ip_addresses_updates_without_resync(self):
        device_tag = create_tags("dynamic-update")[0]
        device = dcim.Device.objects.get(name="Device 1")

        alias = self.model.objects.create(
            name="Object Alias Dynamic Update",
            description="Dynamic targets",
            tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_ALL,
        )
        alias.device_tags.set([device_tag])
        self.assertEqual(alias.get_resolved_ip_addresses().count(), 0)

        device.tags.add(device_tag)
        self.assertEqual(alias.get_resolved_ip_addresses().count(), 2)

        new_ip = ipam.IPAddress.objects.create(address="10.0.9.9/24")
        new_ip.assigned_object = device.interfaces.first()
        new_ip.save()

        self.assertIn(
            "10.0.9.9/24",
            {str(address) for address in alias.get_resolved_ip_addresses().values_list("address", flat=True)},
        )

    def test_qs_contains_dynamic_members(self):
        device_tag, virtual_machine_tag = create_tags("selector-device", "selector-virtual-machine")
        device = dcim.Device.objects.get(name="Device 1")
        virtual_machine = virtualization.VirtualMachine.objects.get(name="VM 2")
        device.tags.add(device_tag)
        virtual_machine.tags.add(virtual_machine_tag)

        alias = self.model.objects.create(
            name="Object Alias Dynamic Match",
            description="Dynamic targets",
            tag_matching_rule=choices.TagMatchingRuleChoices.MATCHING_ALL,
        )
        alias.device_tags.set([device_tag])
        alias.virtual_machine_tags.set([virtual_machine_tag])

        device_ip = ipam.IPAddress.objects.get(address="10.0.1.1/24")
        virtual_machine_ip = ipam.IPAddress.objects.get(address="10.100.1.1/24")

        self.assertIn(alias, self.model.objects.contains(device))
        self.assertIn(alias, self.model.objects.contains(virtual_machine))
        self.assertIn(alias, self.model.objects.contains(device_ip))
        self.assertIn(alias, self.model.objects.contains(virtual_machine_ip))

        self.assertIn(alias, self.model.objects.contains(device, tagged=True))
        self.assertIn(alias, self.model.objects.contains(virtual_machine, tagged=True))
        self.assertIn(alias, self.model.objects.contains(device_ip, tagged=True))
        self.assertIn(alias, self.model.objects.contains(virtual_machine_ip, tagged=True))

        self.assertNotIn(alias, self.model.objects.contains(device, direct=True))
        self.assertNotIn(alias, self.model.objects.contains(device, indirect=True))


class DataFlowTestCase(TestCase):
    model = models.DataFlow

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        cls.dataflows = data.dataflows
        cls.tags = data.tags

    def test_qs_only_disabled(self):
        qs = self.model.objects.only_disabled()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 3)

    def test_qs_only_enabled(self):
        qs = self.model.objects.only_enabled()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 5)

    def test_qs_part_of_group_recursive(self):
        groups = models.DataFlowGroup.objects.all()
        qs = self.model.objects.part_of_group_recursive(groups[1], groups[2], include_direct_children=False)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 1)
        qs = self.model.objects.part_of_group_recursive(groups[1], groups[2], include_direct_children=True)
        self.assertEqual(qs.count(), 1)
        qs = self.model.objects.part_of_group_recursive(groups[2], include_direct_children=False)
        self.assertEqual(qs.count(), 0)
        qs = self.model.objects.part_of_group_recursive(groups[2], include_direct_children=True)
        self.assertEqual(qs.count(), 1)
        qs = self.model.objects.part_of_group_recursive(groups[1], groups[5], include_direct_children=False)
        self.assertEqual(qs.count(), 5)

    def test_qs_sources_empty(self):
        qs = self.model.objects.sources()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 0)

    def test_qs_sources_direct(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.sources(*ips, direct=True)
        self.assertEqual(qs.count(), 1)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.sources(*iprange, direct=True)
        self.assertEqual(qs.count(), 1)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.sources(*pref, direct=True)
        self.assertEqual(qs.count(), 3)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.sources(*dev, direct=True)
        self.assertEqual(qs.count(), 1)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.sources(*vm, direct=True)
        self.assertEqual(qs.count(), 1)

        qs = self.model.objects.sources(pref[0], *vm, direct=True)
        self.assertEqual(qs.count(), 4)

    def test_qs_sources_indirect(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.sources(*ips, indirect=True)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 3)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.sources(*iprange, indirect=True)
        self.assertEqual(qs.count(), 3)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.sources(*pref, indirect=True)
        self.assertEqual(qs.count(), 3)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.sources(*dev, indirect=True)
        self.assertEqual(qs.count(), 3)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.sources(*vm, indirect=True)
        self.assertEqual(qs.count(), 3)

        qs = self.model.objects.sources(pref[0], *vm, indirect=True)
        self.assertEqual(qs.count(), 3)

    def test_qs_destinations_empty(self):
        qs = self.model.objects.destinations()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 0)

    def test_qs_destinations_direct(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.destinations(*ips, direct=True)
        self.assertEqual(qs.count(), 2)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.destinations(*iprange, direct=True)
        self.assertEqual(qs.count(), 1)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.destinations(*pref, direct=True)
        self.assertEqual(qs.count(), 1)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.destinations(*dev, direct=True)
        self.assertEqual(qs.count(), 2)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.destinations(*vm, direct=True)
        self.assertEqual(qs.count(), 3)

        qs = self.model.objects.destinations(pref[0], *vm, direct=True)
        self.assertEqual(qs.count(), 3)

    def test_qs_destinations_indirect(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.destinations(*ips, indirect=True)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 1)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.destinations(*iprange, indirect=True)
        self.assertEqual(qs.count(), 1)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.destinations(*pref, indirect=True)
        self.assertEqual(qs.count(), 1)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.destinations(*dev, indirect=True)
        self.assertEqual(qs.count(), 1)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.destinations(*vm, indirect=True)
        self.assertEqual(qs.count(), 1)

        qs = self.model.objects.destinations(pref[0], *vm, indirect=True)
        self.assertEqual(qs.count(), 1)

    def test_qs_sources_or_destinations_empty(self):
        qs = self.model.objects.sources_or_destinations()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 0)

    def test_qs_sources_or_destinations_direct(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.sources_or_destinations(*ips, direct=True)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 3)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.sources_or_destinations(*iprange, direct=True)
        self.assertEqual(qs.count(), 2)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.sources_or_destinations(*pref, direct=True)
        self.assertEqual(qs.count(), 4)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.sources_or_destinations(*dev, direct=True)
        self.assertEqual(qs.count(), 3)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.sources_or_destinations(*vm, direct=True)
        self.assertEqual(qs.count(), 3)

        qs = self.model.objects.sources_or_destinations(pref[0], *vm, direct=True)
        self.assertEqual(qs.count(), 5)

    def test_qs_sources_or_destinations_indirect(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.sources_or_destinations(*ips, indirect=True)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 4)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.sources_or_destinations(*iprange, indirect=True)
        self.assertEqual(qs.count(), 4)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.sources_or_destinations(*pref, indirect=True)
        self.assertEqual(qs.count(), 4)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.sources_or_destinations(*dev, indirect=True)
        self.assertEqual(qs.count(), 4)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.sources_or_destinations(*vm, indirect=True)
        self.assertEqual(qs.count(), 4)

        qs = self.model.objects.sources_or_destinations(pref[0], *vm, indirect=True)
        self.assertEqual(qs.count(), 4)

    def test_inherited_status(self):
        d = self.model(
            name="New DF 1",
            status=choices.DataFlowStatusChoices.STATUS_ENABLED,
            group=models.DataFlowGroup.objects.filter(status=choices.DataFlowStatusChoices.STATUS_DISABLED).first(),
            protocol=choices.DataFlowProtocolChoices.PROTOCOL_ANY,
        )
        self.assertEqual(
            d.inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED,
        )
        d = self.model(
            name="New DF 2",
            status=choices.DataFlowStatusChoices.STATUS_DISABLED,
            group=models.DataFlowGroup.objects.filter(status=choices.DataFlowStatusChoices.STATUS_DISABLED).first(),
            protocol=choices.DataFlowProtocolChoices.PROTOCOL_ANY,
        )
        self.assertEqual(d.inherited_status, d.status)
        d = self.model(
            name="New DF 3",
            status=choices.DataFlowStatusChoices.STATUS_ENABLED,
            group=models.DataFlowGroup.objects.first(),
            protocol=choices.DataFlowProtocolChoices.PROTOCOL_ANY,
        )
        self.assertEqual(d.inherited_status, d.status)
        d = self.model(
            name="New DF 4",
            status=choices.DataFlowStatusChoices.STATUS_DISABLED,
            group=models.DataFlowGroup.objects.first(),
            protocol=choices.DataFlowProtocolChoices.PROTOCOL_ANY,
        )
        self.assertEqual(d.inherited_status, d.status)

        dataflows = self.dataflows
        self.assertEqual(
            dataflows[0].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_DISABLED,
        )
        self.assertEqual(
            dataflows[1].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_ENABLED,
        )
        self.assertEqual(
            dataflows[2].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED,
        )
        self.assertEqual(
            dataflows[3].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_ENABLED,
        )
        self.assertEqual(
            dataflows[4].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_DISABLED,
        )

    def test_inherited_tags(self):
        dataflows = self.dataflows
        tags = self.tags

        self.assertEqual(set(dataflows[0].inherited_tags), set())
        self.assertEqual(set(dataflows[1].inherited_tags), set(tags[6:7]))

        self.assertEqual(len(dataflows[2].inherited_tags), 5)
        self.assertEqual(set(dataflows[2].inherited_tags), set(tags[0:2]) | set(tags[3:6]))

        for i in [3, 4, 5, 6]:
            self.assertEqual(set(dataflows[i].inherited_tags), set(tags[0:2]))

        self.assertEqual(set(dataflows[7].inherited_tags), set())

    def test_icmp_clean_remove_source_ports(self):
        def rand_source_ports():
            return [random.randrange(0, 255) for i in range(0, random.randrange(0, 12))]

        for type_code, description in choices.ICMPv4TypeChoices:
            d = self.model(
                name=f"ICMPv4 {description}",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                protocol=choices.DataFlowProtocolChoices.PROTOCOL_ICMPv4,
                source_ports=rand_source_ports(),
                destination_ports=[type_code],
            )
            d.clean()
            self.assertEqual(d.source_ports, [], "Cleaning ICMPv4 should clear source_ports")
            self.assertEqual(d.destination_ports, [type_code], "Cleaning ICMPv4 should keep destination_ports")

        for type_code, description in choices.ICMPv6TypeChoices:
            d = self.model(
                name=f"ICMPv6 {description}",
                status=choices.DataFlowStatusChoices.STATUS_ENABLED,
                protocol=choices.DataFlowProtocolChoices.PROTOCOL_ICMPv6,
                source_ports=rand_source_ports(),
                destination_ports=[type_code],
            )
            d.clean()
            self.assertEqual(d.source_ports, [], "Cleaning ICMPv4 should clear source_ports")
            self.assertEqual(d.destination_ports, [type_code], "Cleaning ICMPv4 should keep destination_ports")


class DataFlowGroupTestCase(TestCase):
    model = models.DataFlowGroup

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        cls.groups = data.dataflowgroups
        cls.tags = data.tags

    def test_qs_only_disabled(self):
        qs = self.model.objects.only_disabled()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 5)

    def test_qs_only_enabled(self):
        qs = self.model.objects.only_enabled()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 5)

    def test_inherited_status(self):
        groups = self.groups

        self.assertEqual(
            groups[1].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_DISABLED,
        )
        self.assertEqual(
            groups[2].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_INHERITED_DISABLED,
        )
        self.assertEqual(
            groups[3].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_DISABLED,
        )
        self.assertEqual(
            groups[6].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_ENABLED,
        )
        self.assertEqual(
            groups[7].inherited_status,
            choices.DataFlowInheritedStatusChoices.STATUS_DISABLED,
        )

    def test_inherited_tags(self):
        groups = self.groups
        tags = self.tags

        self.assertEqual(set(groups[0].inherited_tags), set(tags[0:2]))
        self.assertEqual(set(groups[1].inherited_tags), set(tags[0:2]))

        self.assertEqual(len(groups[2].inherited_tags), 3)
        self.assertEqual(set(groups[2].inherited_tags), set(tags[0:2]) | set(tags[3:4]))

        self.assertEqual(set(groups[3].inherited_tags), set(tags[0:3]))

        for i in [4, 5, 6, 7]:
            self.assertEqual(set(groups[i].inherited_tags), set(tags[0:2]))

        self.assertEqual(set(groups[8].inherited_tags), set())
        self.assertEqual(set(groups[9].inherited_tags), set())
