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


class TagSelectorTestCase(TestCase):
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
