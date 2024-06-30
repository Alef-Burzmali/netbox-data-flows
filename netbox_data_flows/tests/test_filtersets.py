from django.test import TestCase

from netbox_data_flows import models, filtersets, choices

from .data import TestData


class ApplicationFilterSetAddin:
    def test_application(self):
        applications = models.Application.objects.all()[:2]
        params = {"application_id": [applications[0].pk, applications[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"application": [applications[0].name, applications[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_application_role(self):
        roles = models.Application.objects.all()[:2]
        params = {"application_role_id": [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"application_role": [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)


class ApplicationRoleFilterSetTestCase(TestCase):
    queryset = models.ApplicationRole.objects.all()
    filterset = filtersets.ApplicationRoleFilterSet

    @classmethod
    def setUpTestData(cls):
        TestData.create_applicationroles()

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


class ApplicationFilterSetTestCase(TestCase):
    queryset = models.Application.objects.all()
    filterset = filtersets.ApplicationFilterSet

    @classmethod
    def setUpTestData(cls):
        TestData.create_applications()

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


class DataFlowGroupFilterSetTestCase(TestCase):
    queryset = models.DataFlowGroup.objects.all()
    filterset = filtersets.DataFlowGroupFilterSet

    @classmethod
    def setUpTestData(cls):
        TestData.create_dataflowgroups()

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
        params = {
            "inherited_status": choices.DataFlowStatusChoices.STATUS_ENABLED
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {
            "inherited_status": choices.DataFlowStatusChoices.STATUS_DISABLED
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

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
