from django.test import TestCase, override_settings
from django.urls import reverse
from netaddr import IPNetwork

from core.models import ObjectType
from extras.models import Tag
from users.models import ObjectPermission, User

from dcim.models import Device, DeviceRole, DeviceType, Interface, Manufacturer, Site
from ipam.models import IPAddress, IPRange, Prefix
from virtualization.models import VirtualMachine, VMInterface

from netbox_data_flows.models import DataFlow, ObjectAlias


@override_settings(EXEMPT_VIEW_PERMISSIONS=[], EXEMPT_EXCLUDE_MODELS=[], DEFAULT_PERMISSIONS={})
class RelatedObjectPermissionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(name="Manufacturer", slug="manufacturer")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Device type", slug="device-type")
        role = DeviceRole.objects.create(name="Role", slug="role")
        site = Site.objects.create(name="Site", slug="site")
        cls.device = Device.objects.create(name="Device", device_type=device_type, role=role, site=site)
        cls.vm = VirtualMachine.objects.create(name="VM")
        interfaces = (
            Interface.objects.create(device=cls.device, name="eth0", type="1000base-t"),
            VMInterface.objects.create(virtual_machine=cls.vm, name="eth0"),
        )
        cls.addresses = tuple(
            IPAddress.objects.create(address=f"192.0.2.{index}/32", assigned_object=interface)
            for index, interface in enumerate(interfaces, 1)
        )
        cls.prefixes = (
            Prefix.objects.create(prefix="192.0.2.0/24"),
            Prefix.objects.create(prefix="198.51.100.0/24"),
        )
        cls.ranges = (
            IPRange.objects.create(start_address=IPNetwork("192.0.2.1/32"), end_address=IPNetwork("192.0.2.10/32")),
            IPRange.objects.create(
                start_address=IPNetwork("198.51.100.1/32"), end_address=IPNetwork("198.51.100.10/32")
            ),
        )
        parent_prefix = Prefix.objects.create(prefix="192.0.0.0/16")
        tag = Tag.objects.create(name="Machine tag", slug="machine-tag")
        cls.device.tags.add(tag)
        cls.vm.tags.add(tag)

        cls.direct = ObjectAlias.objects.create(name="Direct alias")
        cls.direct.ip_addresses.set(cls.addresses)
        cls.direct.prefixes.set(cls.prefixes)
        cls.direct.ip_ranges.set(cls.ranges)
        cls.indirect = ObjectAlias.objects.create(name="Indirect alias")
        cls.indirect.prefixes.add(parent_prefix)
        cls.tagged = ObjectAlias.objects.create(name="Tagged alias", tag_matching_rule="all")
        cls.tagged.device_tags.add(tag)
        cls.tagged.virtual_machine_tags.add(tag)
        cls.aliases = (cls.direct, cls.indirect, cls.tagged)
        cls.flows = []
        for index, alias in enumerate(cls.aliases, 1):
            flow = DataFlow.objects.create(name=f"Flow {index}")
            flow.sources.add(alias)
            flow.destinations.add(alias)
            cls.flows.append(flow)
        cls.extra_flow = DataFlow.objects.create(name="Forbidden extra flow")
        cls.extra_flow.sources.add(cls.direct)
        cls.extra_flow.destinations.add(cls.direct)
        cls.parents = (cls.device, cls.vm, cls.addresses[0], cls.prefixes[0], cls.ranges[0])

    def login_with_permissions(self, *grants):
        user = User.objects.create_user(username=f"reader-{User.objects.count()}")
        for model, constraints in grants:
            permission = ObjectPermission.objects.create(
                name="View permission", actions=["view"], constraints=constraints
            )
            permission.object_types.add(ObjectType.objects.get_for_model(model))
            permission.users.add(user)
        self.client.force_login(user)
        return user

    def tab_url(self, parent):
        return reverse(f"{parent._meta.app_label}:{parent._meta.model_name}_dataflows-tab", args=[parent.pk])

    def assert_hidden(self, response, value):
        self.assertEqual(response.status_code, 200)
        # Avoid dumping whole responses (including CSRF tokens) if the regression fails.
        self.assertFalse(str(value).encode() in response.content, f"Response discloses forbidden value: {value}")

    def test_model_tabs_require_dataflow_permission(self):
        for parent in self.parents:
            with self.subTest(parent=parent):
                self.login_with_permissions((type(parent), {"pk": parent.pk}))
                self.assertEqual(self.client.get(self.tab_url(parent)).status_code, 403)

    def test_model_tabs_preserve_parent_permission_constraints(self):
        self.login_with_permissions((Device, {"pk": -1}), (DataFlow, {}))
        self.assertEqual(self.client.get(self.tab_url(self.device)).status_code, 404)

    def test_model_tabs_restrict_each_matching_type(self):
        for index, (alias, flow) in enumerate(zip(self.aliases, self.flows)):
            parents = self.parents[:3] if alias == self.tagged else self.parents
            for parent in parents:
                with self.subTest(alias=alias, parent=parent):
                    self.login_with_permissions(
                        (type(parent), {"pk": parent.pk}),
                        (DataFlow, {"pk": flow.pk}),
                        (ObjectAlias, {"pk": alias.pk}),
                    )
                    response = self.client.get(self.tab_url(parent))
                    self.assertContains(response, flow.name)
                    self.assertContains(response, alias.name)
                    self.assert_hidden(response, self.extra_flow.name)
                    for other_index, other_alias in enumerate(self.aliases):
                        if index != other_index:
                            self.assert_hidden(response, other_alias.name)

    def test_flow_tables_and_detail_restrict_alias_names(self):
        self.login_with_permissions((Device, {"pk": self.device.pk}), (DataFlow, {"pk": self.flows[0].pk}))
        urls = (
            self.tab_url(self.device),
            self.flows[0].get_absolute_url(),
            reverse("plugins:netbox_data_flows:dataflow_list"),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, self.flows[0].name)
                self.assert_hidden(response, self.direct.name)
                self.assert_hidden(response, self.direct.get_absolute_url())

    def test_alias_dataflows_tab_requires_dataflow_permission(self):
        self.login_with_permissions((ObjectAlias, {"pk": self.direct.pk}))
        url = reverse("plugins:netbox_data_flows:objectalias_objectalias-dataflows-tab", args=[self.direct.pk])
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_alias_detail_hides_unpermitted_ipam_members_and_counts(self):
        for alias in (self.direct, self.tagged):
            with self.subTest(alias=alias):
                self.login_with_permissions((ObjectAlias, {"pk": alias.pk}))
                response = self.client.get(alias.get_absolute_url())
                for value in (*self.addresses, *self.prefixes, *self.ranges):
                    self.assert_hidden(response, value)
                for name in ("prefix_count", "ip_range_count", "ip_address_count", "resolved_ip_address_count"):
                    self.assertEqual(response.context[name], 0)

    def test_alias_detail_respects_constrained_ipam_permissions(self):
        for alias in (self.direct, self.tagged):
            with self.subTest(alias=alias):
                self.login_with_permissions(
                    (ObjectAlias, {"pk": alias.pk}),
                    (IPAddress, {"pk": self.addresses[0].pk}),
                    (Prefix, {"pk": self.prefixes[0].pk}),
                    (IPRange, {"pk": self.ranges[0].pk}),
                )
                response = self.client.get(alias.get_absolute_url())
                self.assertContains(response, str(self.addresses[0]))
                self.assert_hidden(response, self.addresses[1])
                self.assert_hidden(response, self.prefixes[1])
                self.assert_hidden(response, self.ranges[1])
                if alias == self.direct:
                    for name in ("prefix_count", "ip_range_count", "ip_address_count"):
                        self.assertEqual(response.context[name], 1)
                else:
                    self.assertEqual(response.context["resolved_ip_address_count"], 1)

    def test_flow_targets_hide_unpermitted_ipam_members(self):
        for flow in (self.flows[0], self.flows[2]):
            with self.subTest(flow=flow):
                self.login_with_permissions((DataFlow, {"pk": flow.pk}))
                response = self.client.get(reverse("plugins:netbox_data_flows:dataflow_targets", args=[flow.pk]))
                for value in (*self.addresses, *self.prefixes, *self.ranges):
                    self.assert_hidden(response, value)

    def test_flow_targets_preserve_permitted_ipam_members(self):
        for flow in (self.flows[0], self.flows[2]):
            with self.subTest(flow=flow):
                self.login_with_permissions(
                    (DataFlow, {"pk": flow.pk}),
                    (IPAddress, {"pk": self.addresses[0].pk}),
                    (Prefix, {"pk": self.prefixes[0].pk}),
                    (IPRange, {"pk": self.ranges[0].pk}),
                )
                response = self.client.get(reverse("plugins:netbox_data_flows:dataflow_targets", args=[flow.pk]))
                self.assertContains(response, str(self.addresses[0]))
                self.assert_hidden(response, self.addresses[1])
                for direction in ("sources", "destinations"):
                    self.assertEqual(len(response.context[f"{direction}_ip_addresses_table"].data), 1)
                    for kind in ("prefixes", "ip_ranges"):
                        expected = 1 if flow == self.flows[0] else 0
                        self.assertEqual(len(response.context[f"{direction}_{kind}_table"].data), expected)
