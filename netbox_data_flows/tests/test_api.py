from django.urls import reverse

from utilities.testing import APITestCase
from utilities.testing import APIViewTestCases as _APIViewTestCases

from ipam import models as ipam

from netbox_data_flows import choices, models

from .data import TestData


class PluginUrlBase:
    view_namespace = "plugins-api:netbox_data_flows"


class APIViewTestCases(_APIViewTestCases):
    class APIViewTestCaseNoGraphQL(_APIViewTestCases.APIViewTestCase):
        def test_graphql_get_object(self):
            self.skipTest("GraphQL not supported")

        def test_graphql_list_objects(self):
            self.skipTest("GraphQL not supported")

        def test_graphql_filter_objects(self):
            self.skipTest("GraphQL not supported")


class AppTest(PluginUrlBase, APITestCase):

    def test_root(self):
        url = reverse(f"{self.view_namespace}-api:api-root")
        response = self.client.get("{}?format=api".format(url), **self.header)
        self.assertEqual(response.status_code, 200)


class ApplicationRoleTestCase(PluginUrlBase, APIViewTestCases.APIViewTestCaseNoGraphQL):
    model = models.ApplicationRole
    brief_fields = [
        "description",
        "display",
        "id",
        "name",
        "slug",
        "url",
    ]

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        data.applicationroles

        cls.create_data = [
            {
                "name": "Application Role 4",
                "slug": "application-role-4",
            },
            {
                "name": "Application Role 5",
                "slug": "application-role-5",
            },
            {
                "name": "Application Role 6",
                "slug": "application-role-6",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
        }


class ApplicationTestCase(PluginUrlBase, APIViewTestCases.APIViewTestCaseNoGraphQL):
    model = models.Application
    brief_fields = [
        "description",
        "display",
        "id",
        "name",
        "url",
    ]

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        roles = data.applicationroles
        data.applications

        cls.create_data = [
            {
                "name": "Application 10",
                "description": "Description 1",
                "role": roles[0].pk,
            },
            {
                "name": "Application 11",
                "role": roles[1].pk,
            },
            {
                "name": "Application 12",
                "comments": "New comments",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
            "role": roles[2].pk,
        }


class DataFlowGroupTestCase(PluginUrlBase, APIViewTestCases.APIViewTestCaseNoGraphQL):
    model = models.DataFlowGroup
    brief_fields = [
        "description",
        "display",
        "id",
        "name",
        "slug",
        "status",
        "url",
    ]

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        apps = data.applications
        groups = data.dataflowgroups

        cls.create_data = [
            {
                "name": "Group 20",
                "slug": "group-20",
                "description": "Description 1",
                "application": apps[0].pk,
                "status": choices.DataFlowStatusChoices.STATUS_ENABLED,
            },
            {
                "name": "Group 21",
                "slug": "group-21",
                "parent": groups[3].pk,
                "status": choices.DataFlowStatusChoices.STATUS_DISABLED,
            },
            {
                "name": "Group 22",
                "slug": "group-22",
                "application": apps[1].pk,
                "parent": groups[1].pk,
                "comments": "New comments",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
            "application": apps[0].pk,
            "status": choices.DataFlowStatusChoices.STATUS_DISABLED,
            "comments": "New comments",
        }


class ObjectAliasTestCase(PluginUrlBase, APIViewTestCases.APIViewTestCaseNoGraphQL):
    model = models.ObjectAlias
    brief_fields = [
        "description",
        "display",
        "id",
        "name",
        "url",
    ]

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        data.objectaliases

        ip_addresses = [
            ipam.IPAddress(address="192.168.0.1/24"),
            ipam.IPAddress(address="192.168.0.2/24"),
        ]
        ipam.IPAddress.objects.bulk_create(ip_addresses)
        ip_ranges = [
            ipam.IPRange(
                start_address="192.168.0.5/24",
                end_address="192.168.0.10/24",
                size=5,
            ),
        ]
        ipam.IPRange.objects.bulk_create(ip_ranges)
        prefixes = [
            ipam.Prefix(prefix="192.168.0.0/24"),
        ]
        ipam.Prefix.objects.bulk_create(prefixes)

        cls.create_data = [
            {
                "name": "Object Alias 20",
                "description": "Description 1",
            },
            {
                "name": "Object Alias 21",
                "prefixes": [o.pk for o in prefixes],
                "ip_ranges": [o.pk for o in ip_ranges],
                "ip_addresses": [o.pk for o in ip_addresses],
            },
            {
                "name": "Object Alias 22",
                "comments": "New comments",
                "ip_addresses": [ip_addresses[0].pk],
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
            "comments": "New comments",
            "prefixes": [o.pk for o in prefixes],
        }


class DataFlowTestCase(PluginUrlBase, APIViewTestCases.APIViewTestCaseNoGraphQL):
    model = models.DataFlow
    brief_fields = [
        "description",
        "display",
        "id",
        "name",
        "url",
    ]

    @classmethod
    def setUpTestData(cls):
        data = TestData()
        apps = data.applications
        groups = data.dataflowgroups
        aliases = data.objectaliases
        data.dataflows

        cls.create_data = [
            {
                "name": "Data Flow 20",
                "description": "Description 1",
                "application": apps[0].pk,
                "group": groups[1].pk,
                "status": choices.DataFlowStatusChoices.STATUS_ENABLED,
                "protocol": choices.DataFlowProtocolChoices.PROTOCOL_TCP,
                "source_ports": [1, 2, 3],
                "destination_ports": [4, 5, 6],
                "comments": "New comments",
                "sources": [aliases[0].pk, aliases[1].pk],
                "destinations": [aliases[2].pk, aliases[3].pk],
            },
            {
                "name": "Data Flow 21",
                "protocol": choices.DataFlowProtocolChoices.PROTOCOL_ANY,
            },
            {
                "name": "Data Flow 22",
                "application": None,
                "group": groups[2].pk,
                "protocol": choices.DataFlowProtocolChoices.PROTOCOL_UDP,
                "sources": [aliases[1].pk],
                "source_ports": [5],
                "destination_ports": [],
            },
            {
                "name": "Data Flow 22",
                "application": apps[2].pk,
                "group": None,
                "protocol": choices.DataFlowProtocolChoices.PROTOCOL_TCP_UDP,
                "sources": [],
                "destinations": [aliases[1].pk],
                "destination_ports": [155, 156],
            },
        ]
        cls.bulk_update_data = {
            "description": "Description 1",
            "application": apps[0].pk,
            "group": groups[1].pk,
            "status": choices.DataFlowStatusChoices.STATUS_ENABLED,
            "protocol": choices.DataFlowProtocolChoices.PROTOCOL_TCP,
            "source_ports": [1, 2, 3],
            "destination_ports": [4, 5, 6],
            "comments": "New comments",
            "sources": [aliases[0].pk, aliases[1].pk],
            "destinations": [aliases[2].pk, aliases[3].pk],
        }
