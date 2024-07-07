from django.urls import reverse

# from rest_framework import status

from utilities.testing import APITestCase
from utilities.testing import APIViewTestCases as _APIViewTestCases

from ipam import models as ipam

from netbox_data_flows import models, choices

from .data import TestData


class PluginUrlBase:
    view_namespace = "plugins-api:netbox_data_flows"


class APIViewTestCases(_APIViewTestCases):
    class APIViewTestClassNoGraphQL(
        _APIViewTestCases.GetObjectViewTestCase,
        _APIViewTestCases.ListObjectsViewTestCase,
        _APIViewTestCases.CreateObjectViewTestCase,
        _APIViewTestCases.UpdateObjectViewTestCase,
        _APIViewTestCases.DeleteObjectViewTestCase,
    ):
        pass


class AppTest(PluginUrlBase, APITestCase):

    def test_root(self):
        url = reverse(f"{self.view_namespace}-api:api-root")
        response = self.client.get("{}?format=api".format(url), **self.header)
        self.assertEqual(response.status_code, 200)


class ApplicationRoleTestCase(
    PluginUrlBase, APIViewTestCases.APIViewTestClassNoGraphQL
):
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
        TestData.create_applicationroles()

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


class ApplicationTestCase(
    PluginUrlBase, APIViewTestCases.APIViewTestClassNoGraphQL
):
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
        roles = TestData.create_applicationroles()
        TestData.create_applications()

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


class DataFlowGroupTestCase(
    PluginUrlBase, APIViewTestCases.APIViewTestClassNoGraphQL
):
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
        apps = TestData.create_applications()
        groups = TestData.create_dataflowgroups()

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


class ObjectAliasTargetTestCase(
    PluginUrlBase, APIViewTestCases.APIViewTestClassNoGraphQL
):
    model = models.ObjectAliasTarget
    brief_fields = [
        "display",
        "id",
        "url",
    ]

    def assertInstanceEqual(self, instance, data, exclude=None, api=True):
        if exclude is None:
            exclude = []
        exclude += ["target"]

        super().assertInstanceEqual(instance, data, exclude=exclude, api=api)

        if "target" in data:
            self.assertEqual(
                data["target"]["object_type"],
                f"{instance.target._meta.app_label}.{instance.target._meta.model_name}",
            )
            self.assertEqual(data["target"]["object_id"], instance.target.pk)

    @classmethod
    def setUpTestData(cls):
        TestData.create_objectaliastargets()

        ipaddresses = [
            ipam.IPAddress(address="192.168.0.1/24"),
            ipam.IPAddress(address="192.168.0.2/24"),
        ]
        ipam.IPAddress.objects.bulk_create(ipaddresses)
        ipranges = [
            ipam.IPRange(
                start_address="192.168.0.5/24",
                end_address="192.168.0.10/24",
                size=5,
            ),
        ]
        ipam.IPRange.objects.bulk_create(ipranges)
        prefixes = [
            ipam.Prefix(prefix="192.168.0.0/24"),
        ]
        ipam.Prefix.objects.bulk_create(prefixes)

        def get_type(model):
            return f"{model._meta.app_label}.{model._meta.model_name}"

        cls.create_data = [
            {
                "target": {
                    "object_type": get_type(ipam.IPAddress),
                    "object_id": ipaddresses[0].pk,
                }
            },
            {
                "target": {
                    "object_type": get_type(ipam.IPAddress),
                    "object_id": ipaddresses[1].pk,
                }
            },
            {
                "target": {
                    "object_type": get_type(ipam.IPRange),
                    "object_id": ipranges[0].pk,
                }
            },
            {
                "target": {
                    "object_type": get_type(ipam.Prefix),
                    "object_id": prefixes[0].pk,
                }
            },
        ]

    def test_bulk_update_objects(self):
        # skip
        pass


class ObjectAliasTestCase(
    PluginUrlBase, APIViewTestCases.APIViewTestClassNoGraphQL
):
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
        targets = TestData.create_objectaliastargets()
        TestData.create_objectaliases()

        cls.create_data = [
            {
                "name": "Object Alias 20",
                "description": "Description 1",
            },
            {
                "name": "Object Alias 21",
                "targets": [o.pk for o in targets[0:5]],
            },
            {
                "name": "Object Alias 22",
                "comments": "New comments",
            },
        ]
        cls.bulk_update_data = {
            "description": "New description",
            "comments": "New comments",
            "targets": [o.pk for o in targets[0:5]],
        }


class DataFlowTestCase(
    PluginUrlBase, APIViewTestCases.APIViewTestClassNoGraphQL
):
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
        apps = TestData.create_applications()
        groups = TestData.create_dataflowgroups()
        aliases = TestData.create_objectaliases()
        TestData.create_dataflows()

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
