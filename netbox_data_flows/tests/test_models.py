from django.db.models import QuerySet
from django.test import TestCase

from dcim import models as dcim
from ipam import models as ipam
from virtualization import models as virtualization

from netbox_data_flows import choices, models

from .data import TestData


class ObjectAliasTargetTestCase(TestCase):
    model = models.ObjectAliasTarget

    @classmethod
    def setUpTestData(cls):
        TestData.create_objectaliastargets()

    def test_objectalias_assignment_coherency(self):
        from netbox_data_flows.models.objectaliases import OBJECTALIAS_ASSIGNMENT_MODELS, OBJECTALIAS_ASSIGNMENT_OBJECTS

        models = tuple((m._meta.app_label, m._meta.model_name) for m in OBJECTALIAS_ASSIGNMENT_OBJECTS)
        self.assertEqual(
            models,
            OBJECTALIAS_ASSIGNMENT_MODELS,
            "Model object list differs from model label list",
        )

    def test_get_or_create_new_targets(self):
        obj = ipam.IPAddress.objects.create(address="1.2.3.4/24")
        t = self.model.get_or_create(obj)
        self.assertIsNotNone(t)
        self.assertIsNone(t.pk)
        self.assertEqual(t.target, obj)

        obj = ipam.IPRange(
            start_address="1.2.3.5/24",
            end_address="1.2.3.10/24",
            size=40,
        )
        ipam.IPRange.objects.bulk_create([obj])
        t = self.model.get_or_create(obj)
        self.assertIsNotNone(t)
        self.assertIsNone(t.pk)
        self.assertEqual(t.target, obj)

        obj = ipam.Prefix.objects.create(prefix="1.2.3.0/24")
        t = self.model.get_or_create(obj)
        self.assertIsNotNone(t)
        self.assertIsNone(t.pk)
        self.assertEqual(t.target, obj)

    def test_get_or_create_existing_targets(self):
        obj = ipam.IPAddress.objects.first()
        t = self.model.get_or_create(obj)
        self.assertIsNotNone(t.pk)
        self.assertEqual(t.target, obj)

        obj = ipam.IPRange.objects.first()
        t = self.model.get_or_create(obj)
        self.assertIsNotNone(t.pk)
        self.assertEqual(t.target, obj)

        obj = ipam.Prefix.objects.first()
        t = self.model.get_or_create(obj)
        self.assertIsNotNone(t.pk)
        self.assertEqual(t.target, obj)

    def test_qs_contains(self):
        ips = ipam.IPAddress.objects.all()[:3]
        qs = self.model.objects.contains(*ips)
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 3)
        iprange = ipam.IPRange.objects.all()[:1]
        qs = self.model.objects.contains(*iprange)
        self.assertEqual(qs.count(), 1)
        pref = ipam.Prefix.objects.all()[:2]
        qs = self.model.objects.contains(*pref)
        self.assertEqual(qs.count(), 2)

        dev = dcim.Device.objects.all()[:2]
        qs = self.model.objects.contains(*dev)
        self.assertEqual(qs.count(), 3)
        vm = virtualization.VirtualMachine.objects.all()[:2]
        qs = self.model.objects.contains(*vm)
        self.assertEqual(qs.count(), 3)

        qs = self.model.objects.contains(pref[0], *vm)
        self.assertEqual(qs.count(), 4)

    def test_get_absolute_url(self):
        for t in self.model.objects.all():
            self.assertIsInstance(t.get_absolute_url(), str)

    def test_name(self):
        for t in self.model.objects.all():
            self.assertIn(str(t), t.name)

    def test_parent(self):
        targets = TestData.create_objectaliastargets()

        # Prefixes
        self.assertIsNone(targets[0].parent)
        self.assertEqual(targets[3].parent, ipam.VLAN.objects.first())

        # IP Ranges
        self.assertIsNone(targets[5].parent)

        # IP
        self.assertEqual(targets[7].parent, dcim.Device.objects.first())
        self.assertEqual(targets[9].parent, virtualization.VirtualMachine.objects.first())
        self.assertIsNone(targets[13].parent)


class ObjectAliasTestCase(TestCase):
    model = models.ObjectAlias

    @classmethod
    def setUpTestData(cls):
        TestData.create_objectaliases()

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
        TestData.create_dataflows()

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

        dataflows = TestData.create_dataflows()
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


class DataFlowGroupTestCase(TestCase):
    model = models.DataFlowGroup

    @classmethod
    def setUpTestData(cls):
        TestData.create_dataflowgroups()

    def test_qs_only_disabled(self):
        qs = self.model.objects.only_disabled()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 5)

    def test_qs_only_enabled(self):
        qs = self.model.objects.only_enabled()
        self.assertIsInstance(qs, QuerySet)
        self.assertEqual(qs.count(), 5)

    def test_inherited_status(self):
        groups = self.model.objects.all()
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
