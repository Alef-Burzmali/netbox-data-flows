import random

from django.db.models import QuerySet
from django.test import TestCase

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

    def test_qs_contains(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.contains(*ips)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 2)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.contains(*iprange)
        self.assertEqual(qs.count(), 1)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.contains(*pref)
        self.assertEqual(qs.count(), 2)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.contains(*dev)
        self.assertEqual(qs.count(), 2)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.contains(*vm)
        self.assertEqual(qs.count(), 2)

        qs = self.model.objects.contains(pref[0], *vm)
        self.assertEqual(qs.count(), 4)


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

    def test_qs_sources(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.sources(*ips)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 1)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.sources(*iprange)
        self.assertEqual(qs.count(), 1)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.sources(*pref)
        self.assertEqual(qs.count(), 3)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.sources(*dev)
        self.assertEqual(qs.count(), 1)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.sources(*vm)
        self.assertEqual(qs.count(), 1)

        qs = self.model.objects.sources(pref[0], *vm)
        self.assertEqual(qs.count(), 4)

    def test_qs_destinations(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.destinations(*ips)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 2)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.destinations(*iprange)
        self.assertEqual(qs.count(), 1)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.destinations(*pref)
        self.assertEqual(qs.count(), 1)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.destinations(*dev)
        self.assertEqual(qs.count(), 2)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.destinations(*vm)
        self.assertEqual(qs.count(), 3)

        qs = self.model.objects.destinations(pref[0], *vm)
        self.assertEqual(qs.count(), 3)

    def test_qs_sources_or_destinations(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.sources_or_destinations(*ips)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 3)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.sources_or_destinations(*iprange)
        self.assertEqual(qs.count(), 2)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.sources_or_destinations(*pref)
        self.assertEqual(qs.count(), 4)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.sources_or_destinations(*dev)
        self.assertEqual(qs.count(), 3)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.sources_or_destinations(*vm)
        self.assertEqual(qs.count(), 3)

        qs = self.model.objects.sources_or_destinations(pref[0], *vm)
        self.assertEqual(qs.count(), 5)

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
