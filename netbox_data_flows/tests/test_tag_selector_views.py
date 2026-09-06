from django.test import TestCase
from django.urls import reverse

from users.models import User
from utilities.testing import create_tags

from netbox_data_flows import models

from .test_tag_selectors import TagSelectorTestData


class TagSelectorViewTestCase(TagSelectorTestData, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = User.objects.create_user(username="tag-selector-admin", is_superuser=True)
        cls.oob = create_tags("view-selector-oob")[0]
        for hosts in cls.hosts:
            for host in hosts[:2]:
                host.interfaces.first().tags.add(cls.oob)
        cls.alias.machine_tag_operator = "all"
        cls.alias.interface_tag_operator = "all"
        cls.alias.save()
        cls.alias.interface_tags.add(cls.oob)
        cls.flow = models.DataFlow.objects.create(name="view-selector-flow")
        cls.flow.sources.add(cls.alias)
        cls.flow.destinations.add(cls.alias)

    def setUp(self):
        self.client.force_login(self.user)

    def test_detail_and_target_pages_show_only_matching_addresses(self):
        urls = (
            self.alias.get_absolute_url(),
            reverse("plugins:netbox_data_flows:dataflow_targets", args=[self.flow.pk]),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                for addresses in self.addresses:
                    self.assertContains(response, str(addresses[0].address))
                    for address in addresses[1:]:
                        self.assertNotContains(response, str(address.address))

    def test_machine_and_ip_tabs_agree_with_resolution(self):
        for hosts, addresses in zip(self.hosts, self.addresses):
            for host, address in zip(hosts, addresses):
                for obj in (host, address):
                    with self.subTest(obj=obj):
                        url = reverse(f"{obj._meta.app_label}:{obj._meta.model_name}_dataflows-tab", args=[obj.pk])
                        response = self.client.get(url)
                        self.assertEqual(response.status_code, 200)
                        if host == hosts[0]:
                            self.assertContains(response, self.alias.name)
                            self.assertContains(response, self.flow.name)
                        else:
                            self.assertNotContains(response, self.alias.name)
                            self.assertNotContains(response, self.flow.name)

    def test_rest_patch_preserves_omitted_selectors_and_can_clear_interfaces(self):
        url = reverse("plugins-api:netbox_data_flows-api:objectalias-detail", args=[self.alias.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([tag["id"] for tag in response.json()["interface_tags"]], [self.oob.pk])
        response = self.client.patch(url, {"description": "updated"}, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        self.alias.refresh_from_db()
        self.assertEqual(self.alias.machine_tag_operator, "all")
        self.assertEqual(self.alias.interface_tag_operator, "all")
        self.assertEqual(list(self.alias.interface_tags.values_list("pk", flat=True)), [self.oob.pk])
        response = self.client.patch(url, {"interface_tags": []}, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertFalse(self.alias.interface_tags.exists())

    def test_rest_flow_filters_agree_with_tagged_membership(self):
        url = reverse("plugins-api:netbox_data_flows-api:dataflow-list")
        for kind, hosts in zip(("devices", "virtual_machines"), self.hosts):
            for index, host in enumerate(hosts):
                for direction in ("source", "destination"):
                    with self.subTest(host=host, direction=direction):
                        response = self.client.get(url, {f"{direction}_{kind}": host.pk, "matching_type": "tagged"})
                        self.assertEqual(response.status_code, 200, response.content)
                        ids = {flow["id"] for flow in response.json()["results"]}
                        self.assertEqual(self.flow.pk in ids, index == 0)

    def test_bulk_edit_preserves_omitted_operators_and_clears_interface_tags(self):
        url = reverse("plugins:netbox_data_flows:objectalias_bulk_edit")
        payload = {"pk": [self.alias.pk], "_apply": True, "description": "bulk updated"}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302, response.content)
        self.alias.refresh_from_db()
        self.assertEqual(self.alias.machine_tag_operator, "all")
        self.assertEqual(self.alias.interface_tag_operator, "all")
        self.assertEqual(list(self.alias.interface_tags.values_list("pk", flat=True)), [self.oob.pk])
        payload["_nullify"] = ["interface_tags"]
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302, response.content)
        self.assertFalse(self.alias.interface_tags.exists())
