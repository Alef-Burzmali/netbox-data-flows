from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from utilities.testing import create_tags

from dcim.models import Device, Interface
from ipam.models import IPAddress
from virtualization.models import VirtualMachine, VMInterface

from netbox_data_flows import choices, filtersets, forms, models
from netbox_data_flows.api.serializers.objectaliases import ObjectAliasSerializer

from .data import TestData


class TagSelectorTestData:
    @classmethod
    def setUpTestData(cls):
        TestData().objectaliases
        cls.alpha, cls.beta = create_tags("selector-alpha", "selector-beta")
        template = Device.objects.first()
        cls.hosts = []
        cls.addresses = []
        for model in (Device, VirtualMachine):
            hosts, addresses = [], []
            for index, tags in enumerate(((cls.alpha, cls.beta), (cls.alpha,), (cls.beta,), ())):
                kwargs = {"name": f"selector-{model._meta.model_name}-{index}"}
                if model is Device:
                    kwargs.update(device_type=template.device_type, role=template.role, site=template.site)
                host = model.objects.create(**kwargs)
                host.tags.set(tags)
                if model is Device:
                    interface = Interface.objects.create(device=host, name="eth0", type="1000base-t")
                else:
                    interface = VMInterface.objects.create(virtual_machine=host, name="eth0")
                address = IPAddress.objects.create(
                    address=f"192.0.2.{1 + index + 10 * len(cls.hosts)}/24", assigned_object=interface
                )
                host.primary_ip4 = address
                if model is Device:
                    host.oob_ip = address
                host.save()
                hosts.append(host)
                addresses.append(address)
            cls.hosts.append(hosts)
            cls.addresses.append(addresses)
        cls.alias = models.ObjectAlias.objects.create(name="selector-alias", tag_matching_rule="all")
        cls.alias.device_tags.set((cls.alpha, cls.beta))
        cls.alias.virtual_machine_tags.set((cls.alpha, cls.beta))

    def resolved_ids(self):
        return set(self.alias.get_resolved_ip_addresses().values_list("pk", flat=True))

    def assert_membership(self, obj, expected):
        self.assertEqual(
            models.ObjectAlias.objects.contains(obj, tagged=True).filter(pk=self.alias.pk).exists(), expected
        )


class TagSelectorTestCase(TagSelectorTestData, TestCase):
    def test_machine_operators(self):
        for operator, indexes in (("any", (0, 1, 2)), ("all", (0,))):
            for rule in ("all", "primary", "oob"):
                with self.subTest(operator=operator, rule=rule):
                    self.alias.machine_tag_operator = operator
                    self.alias.tag_matching_rule = rule
                    self.alias.save()
                    expected = {
                        addresses[index].pk
                        for kind, addresses in enumerate(self.addresses)
                        for index in indexes
                        if rule != "oob" or kind == 0
                    }
                    self.assertEqual(self.resolved_ids(), expected)
                    for hosts, addresses in zip(self.hosts, self.addresses):
                        for host, address in zip(hosts, addresses):
                            self.assert_membership(host, address.pk in expected)
                            self.assert_membership(address, address.pk in expected)

    def test_all_does_not_combine_tags_from_different_machines(self):
        self.alias.machine_tag_operator = "all"
        self.alias.save()
        partial_hosts = [host for hosts in self.hosts for host in hosts[1:3]]
        partial_ips = [ip for addresses in self.addresses for ip in addresses[1:3]]
        for objects in (partial_hosts, partial_ips, partial_hosts + partial_ips):
            with self.subTest(objects=objects):
                self.assertFalse(models.ObjectAlias.objects.contains(*objects, tagged=True).filter(pk=self.alias.pk))

    def test_empty_machine_selectors_and_independent_categories(self):
        self.alias.machine_tag_operator = "all"
        self.alias.save()
        self.alias.device_tags.clear()
        self.alias.virtual_machine_tags.set([self.beta])
        self.assertEqual(self.resolved_ids(), {ip.pk for ip in self.addresses[1][:3:2]})
        self.assert_membership(self.hosts[0][0], False)
        self.alias.virtual_machine_tags.clear()
        self.assertEqual(self.resolved_ids(), set())
        self.assert_membership(self.hosts[1][0], False)

    def test_machine_retagging_and_static_union(self):
        self.alias.machine_tag_operator = "all"
        self.alias.save()
        host = self.hosts[0][1]
        address = self.addresses[0][1]
        host.tags.add(self.beta)
        self.assertIn(address.pk, self.resolved_ids())
        self.assert_membership(host, True)
        host.tags.remove(self.alpha)
        self.assertNotIn(address.pk, self.resolved_ids())
        self.assert_membership(host, False)
        self.alias.ip_addresses.set([address, self.addresses[0][0]])
        self.assertEqual(self.resolved_ids(), {address.pk, self.addresses[0][0].pk, self.addresses[1][0].pk})
        self.assertEqual(self.alias.get_resolved_ip_addresses().count(), 3)

    def test_machine_filtersets_and_dataflows(self):
        self.alias.machine_tag_operator = "all"
        self.alias.save()
        flow = models.DataFlow.objects.create(name="selector-flow")
        flow.sources.add(self.alias)
        flow.destinations.add(self.alias)
        for hosts in self.hosts:
            for index, host in enumerate(hosts):
                field = "devices" if isinstance(host, Device) else "virtual_machines"
                params = {field: [host.pk], "matching_type": ["tagged"]}
                aliases = filtersets.ObjectAliasFilterSet(params, models.ObjectAlias.objects.all())
                self.assertTrue(aliases.is_valid(), aliases.errors)
                self.assertEqual(aliases.qs.filter(pk=self.alias.pk).exists(), index == 0)
                for direction in ("sources", "destinations"):
                    self.assertEqual(
                        getattr(models.DataFlow.objects, direction)(host, tagged=True).filter(pk=flow.pk).exists(),
                        index == 0,
                    )
        aliases = filtersets.ObjectAliasFilterSet({"machine_tag_operator": ["all"]})
        self.assertTrue(aliases.is_valid(), aliases.errors)
        self.assertIn(self.alias, aliases.qs)

    def test_machine_operator_api_defaults_partial_update_and_validation(self):
        serializer = ObjectAliasSerializer(data={"name": "selector-default"})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.save().machine_tag_operator, choices.TagOperatorChoices.OPERATOR_ANY)
        self.alias.machine_tag_operator = "all"
        self.alias.save()
        serializer = ObjectAliasSerializer(self.alias, data={"description": "updated"}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.save().machine_tag_operator, "all")
        serializer = ObjectAliasSerializer(self.alias, data={"machine_tag_operator": "invalid"}, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn("machine_tag_operator", serializer.errors)

    def test_machine_operator_csv(self):
        for value in (None, "", "any", "all"):
            with self.subTest(value=value):
                data = {"name": "csv-alias", "tag_matching_rule": "all"}
                if value is not None:
                    data["machine_tag_operator"] = value
                form = forms.ObjectAliasImportForm(data=data)
                self.assertTrue(form.is_valid(), form.errors)
                self.assertEqual(form.save(commit=False).machine_tag_operator, value or "any")
        self.alias.machine_tag_operator = "all"
        self.alias.save()
        form = forms.ObjectAliasImportForm(
            data={"name": self.alias.name, "tag_matching_rule": "all"}, instance=self.alias
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().machine_tag_operator, "all")

    def test_machine_operator_cloning(self):
        self.alias.machine_tag_operator = "all"
        attrs = self.alias.clone()
        self.assertEqual(attrs["machine_tag_operator"], "all")
        self.assertEqual(set(attrs["device_tags"]), {self.alpha.pk, self.beta.pk})
        self.assertEqual(set(attrs["virtual_machine_tags"]), {self.alpha.pk, self.beta.pk})

    def test_contains_query_count_does_not_grow_with_alias_count(self):
        host = self.hosts[0][0]
        with CaptureQueriesContext(connection) as first:
            list(models.ObjectAlias.objects.contains(host, tagged=True))
        for index in range(5):
            alias = models.ObjectAlias.objects.create(name=f"selector-extra-{index}", machine_tag_operator="all")
            alias.device_tags.set([self.alpha, self.beta])
        with CaptureQueriesContext(connection) as second:
            list(models.ObjectAlias.objects.contains(host, tagged=True))
        self.assertEqual(len(first), len(second))


class InterfaceTagSelectorTestCase(TagSelectorTestData, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.oob, cls.admin, cls.app = create_tags("selector-oob", "selector-admin", "selector-app")
        cls.oob_interfaces = []
        cls.dynamic_addresses = []
        for kind, hosts in enumerate(cls.hosts):
            for index, host in enumerate(hosts):
                host.interfaces.first().tags.add(cls.app)
                interfaces = []
                for name, tag in (("eth1", cls.oob), ("eth2", cls.admin)):
                    if isinstance(host, Device):
                        interface = Interface.objects.create(device=host, name=name, type="1000base-t")
                    else:
                        interface = VMInterface.objects.create(virtual_machine=host, name=name)
                    interface.tags.add(tag)
                    interfaces.append(interface)
                number = 1 + kind * 10 + index
                addresses = [
                    IPAddress.objects.create(address=f"198.51.100.{number}/24", assigned_object=interfaces[0]),
                    IPAddress.objects.create(address=f"2001:db8::{number}/64", assigned_object=interfaces[0]),
                    IPAddress.objects.create(address=f"203.0.113.{number}/24", assigned_object=interfaces[1]),
                ]
                cls.oob_interfaces.append(interfaces[0])
                cls.dynamic_addresses.append(addresses)
        cls.alias.interface_tags.add(cls.oob)
        cls.alias.machine_tag_operator = "all"
        cls.alias.save()

    def test_machine_and_interface_operators_are_independent(self):
        self.alias.interface_tags.add(self.admin)
        for combine in (False, True):
            if combine:
                for interface in self.oob_interfaces:
                    interface.tags.add(self.admin)
            for machine_operator in ("any", "all"):
                for interface_operator in ("any", "all"):
                    with self.subTest(combine=combine, machine=machine_operator, interface=interface_operator):
                        self.alias.machine_tag_operator = machine_operator
                        self.alias.interface_tag_operator = interface_operator
                        self.alias.save()
                        expected = set()
                        for row, addresses in enumerate(self.dynamic_addresses):
                            if row % 4 not in ((0, 1, 2) if machine_operator == "any" else (0,)):
                                continue
                            if interface_operator == "any":
                                expected.update(ip.pk for ip in addresses)
                            elif combine:
                                expected.update(ip.pk for ip in addresses[:2])
                        self.assertEqual(self.resolved_ids(), expected)
                        for hosts, addresses in zip(self.hosts, self.addresses):
                            for host, address in zip(hosts, addresses):
                                self.assert_membership(address, False)
                                host_ips = IPAddress.objects.filter(
                                    assigned_object_type=address.assigned_object_type,
                                    assigned_object_id__in=host.interfaces.all(),
                                )
                                self.assert_membership(
                                    host, bool(set(host_ips.values_list("pk", flat=True)) & expected)
                                )
                        for addresses in self.dynamic_addresses:
                            for address in addresses:
                                self.assert_membership(address, address.pk in expected)

    def test_primary_and_oob_are_intersected_with_interface_tags(self):
        self.alias.tag_matching_rule = "primary"
        self.alias.save()
        self.assertEqual(self.resolved_ids(), set())
        for kind in (0, 1):
            host = self.hosts[kind][0]
            ipv6 = self.dynamic_addresses[kind * 4][1]
            self.assert_membership(host, False)
            host.primary_ip6 = ipv6
            host.save()
            self.assert_membership(host, True)
            self.assert_membership(ipv6, True)
            self.assert_membership(self.addresses[kind][0], False)
        self.assertEqual(self.resolved_ids(), {self.dynamic_addresses[row][1].pk for row in (0, 4)})
        self.alias.tag_matching_rule = "oob"
        self.alias.save()
        self.assertEqual(self.resolved_ids(), set())
        device = self.hosts[0][0]
        device.oob_ip = self.dynamic_addresses[0][0]
        device.save()
        self.assertEqual(self.resolved_ids(), {device.oob_ip_id})
        self.assert_membership(device, True)
        self.assert_membership(self.hosts[1][0], False)
        self.oob_interfaces[0].tags.clear()
        self.assertEqual(self.resolved_ids(), set())
        self.assert_membership(device, False)

    def test_no_global_selection_no_address_fallback_and_static_union(self):
        self.alias.device_tags.clear()
        self.alias.virtual_machine_tags.clear()
        self.assertEqual(self.resolved_ids(), set())
        self.assert_membership(self.hosts[0][0], False)
        self.alias.virtual_machine_tags.set([self.alpha, self.beta])
        empty = VMInterface.objects.create(virtual_machine=self.hosts[1][0], name="empty")
        empty.tags.add(self.admin)
        self.alias.interface_tags.set([self.admin, self.app])
        self.alias.interface_tag_operator = "all"
        self.alias.save()
        self.assertEqual(self.resolved_ids(), set())
        self.assert_membership(self.hosts[1][0], False)
        self.alias.interface_tags.set([self.oob])
        self.alias.ip_addresses.set([self.addresses[0][0], self.dynamic_addresses[4][0]])
        self.assertEqual(
            self.resolved_ids(), {self.addresses[0][0].pk, *(ip.pk for ip in self.dynamic_addresses[4][:2])}
        )
        self.assertEqual(self.alias.get_resolved_ip_addresses().count(), 3)
        self.assertEqual(self.alias.get_resolved_ip_addresses(include_direct_assignments=False).count(), 2)

    def test_retagging_reassignment_and_removing_interface_filter(self):
        address = self.dynamic_addresses[0][0]
        self.assertIn(address.pk, self.resolved_ids())
        self.oob_interfaces[0].tags.clear()
        self.assertNotIn(address.pk, self.resolved_ids())
        self.assert_membership(address, False)
        self.oob_interfaces[0].tags.add(self.oob)
        self.assertIn(address.pk, self.resolved_ids())
        address.assigned_object = self.hosts[0][0].interfaces.get(name="eth0")
        address.save()
        self.assertNotIn(address.pk, self.resolved_ids())
        self.assert_membership(address, False)
        self.alias.interface_tags.clear()
        expected = {
            *(ip.pk for row in (0, 4) for ip in self.dynamic_addresses[row]),
            self.addresses[0][0].pk,
            self.addresses[1][0].pk,
        }
        self.assertEqual(self.resolved_ids(), expected)
        self.assert_membership(address, True)

    def test_interface_identity_includes_object_type(self):
        shared_id = max(Interface.objects.latest("pk").pk, VMInterface.objects.latest("pk").pk) + 100
        physical = Interface.objects.create(pk=shared_id, device=self.hosts[0][0], name="same-id", type="1000base-t")
        virtual = VMInterface.objects.create(pk=shared_id, virtual_machine=self.hosts[1][0], name="same-id")
        virtual.tags.add(self.oob)
        excluded = IPAddress.objects.create(address="192.0.2.200/24", assigned_object=physical)
        included = IPAddress.objects.create(address="192.0.2.201/24", assigned_object=virtual)
        self.assertIn(included.pk, self.resolved_ids())
        self.assertNotIn(excluded.pk, self.resolved_ids())
        self.assert_membership(included, True)
        self.assert_membership(excluded, False)

    def test_parent_interface_tags_do_not_select_child_addresses(self):
        for kind in (0, 1):
            host = self.hosts[kind][0]
            interface = host.interfaces.get(name="eth0")
            interface.parent = self.oob_interfaces[kind * 4]
            interface.save()
            address = self.addresses[kind][0]
            self.assertNotIn(address.pk, self.resolved_ids())
            self.assert_membership(address, False)
            interface.tags.add(self.oob)
            self.assertIn(address.pk, self.resolved_ids())
            self.assert_membership(address, True)

    def test_status_and_address_family_are_not_implicitly_filtered(self):
        interface = self.oob_interfaces[0]
        interface.enabled = False
        interface.save()
        address = self.dynamic_addresses[0][0]
        address.status = "reserved"
        address.save()
        self.assertIn(address.pk, self.resolved_ids())
        self.assertIn(self.dynamic_addresses[0][1].pk, self.resolved_ids())
        self.assert_membership(address, True)

    def test_interface_api_partial_updates_defaults_and_validation(self):
        serializer = ObjectAliasSerializer(data={"name": "interface-default"})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        alias = serializer.save()
        self.assertEqual(alias.interface_tag_operator, "any")
        self.assertFalse(alias.interface_tags.exists())
        self.alias.interface_tag_operator = "all"
        self.alias.save()
        for payload in ({"description": "updated"}, {"interface_tags": []}):
            serializer = ObjectAliasSerializer(self.alias, data=payload, partial=True)
            self.assertTrue(serializer.is_valid(), serializer.errors)
            alias = serializer.save()
            self.assertEqual(alias.interface_tag_operator, "all")
            self.assertEqual(alias.machine_tag_operator, "all")
            self.assertEqual(alias.interface_tags.exists(), "interface_tags" not in payload)
        for payload in ({"interface_tag_operator": "invalid"}, {"interface_tags": [999999999]}):
            serializer = ObjectAliasSerializer(self.alias, data=payload, partial=True)
            self.assertFalse(serializer.is_valid())
        serializer = ObjectAliasSerializer(
            self.alias, data={"interface_tags": [self.oob.pk], "interface_tag_operator": "any"}, partial=True
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        alias = serializer.save()
        self.assertEqual(list(alias.interface_tags.values_list("pk", flat=True)), [self.oob.pk])
        self.assertEqual(alias.interface_tag_operator, "any")

    def test_interface_csv_cloning_and_filters(self):
        self.alias.interface_tag_operator = "all"
        self.alias.save()
        attrs = self.alias.clone()
        self.assertEqual(attrs["interface_tags"], [self.oob.pk])
        self.assertEqual(attrs["interface_tag_operator"], "all")
        for value in (None, "", "any", "all"):
            data = {"name": "csv-interface", "tag_matching_rule": "all"}
            if value is not None:
                data["interface_tag_operator"] = value
            form = forms.ObjectAliasImportForm(data=data)
            self.assertTrue(form.is_valid(), form.errors)
            self.assertEqual(form.save(commit=False).interface_tag_operator, value or "any")
        form = forms.ObjectAliasImportForm(
            data={"name": self.alias.name, "tag_matching_rule": "all"}, instance=self.alias
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().interface_tag_operator, "all")
        for params in ({"interface_tags": [self.oob.pk]}, {"interface_tag_operator": ["all"]}):
            aliases = filtersets.ObjectAliasFilterSet(params)
            self.assertTrue(aliases.is_valid(), aliases.errors)
            self.assertIn(self.alias, aliases.qs)

    def test_interface_contains_query_count_does_not_grow_with_alias_count(self):
        host = self.hosts[0][0]
        list(models.ObjectAlias.objects.contains(host, tagged=True))
        with CaptureQueriesContext(connection) as first:
            list(models.ObjectAlias.objects.contains(host, tagged=True))
        for index in range(5):
            alias = models.ObjectAlias.objects.create(name=f"interface-extra-{index}", machine_tag_operator="all")
            alias.device_tags.set([self.alpha, self.beta])
            alias.interface_tags.add(self.oob)
        with CaptureQueriesContext(connection) as second:
            list(models.ObjectAlias.objects.contains(host, tagged=True))
        self.assertEqual(len(first), len(second))
