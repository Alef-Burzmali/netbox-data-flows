from django.test import TestCase

from netbox_data_flows import models, filtersets


class ApplicationRoleFilterSetTestCase(TestCase):
    queryset = models.ApplicationRole.objects.all()
    filterset = filtersets.ApplicationRoleFilterSet

    @classmethod
    def setUpTestData(cls):
        roles = (
            models.ApplicationRole(
                name="Application Role 1",
                slug="application-role-1",
                description="foobar 1",
            ),
            models.ApplicationRole(
                name="Application Role 2",
                slug="application-role-2",
                description="foobar 2",
            ),
            models.ApplicationRole(
                name="Application Role 3",
                slug="application-role-3",
                description="foobar 3",
            ),
        )
        for obj in roles:
            obj.save()

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
        roles = (
            models.ApplicationRole(
                name="Application Role 1",
                slug="application-role-1",
                description="foobar 1",
            ),
            models.ApplicationRole(
                name="Application Role 2",
                slug="application-role-2",
                description="foobar 2",
            ),
            models.ApplicationRole(
                name="Application Role 3",
                slug="application-role-3",
                description="foobar 3",
            ),
        )
        for obj in roles:
            obj.save()

        applications = (
            models.Application(
                name="Application 1", description="barfoo 1", role=roles[0]
            ),
            models.Application(
                name="Application 2", description="barfoo 2", role=roles[1]
            ),
            models.Application(
                name="Application 3", description="barfoo 3", role=roles[1]
            ),
            models.Application(
                name="Application 4", description="barfoo 4", role=roles[2]
            ),
            models.Application(
                name="Application 5", description="barfoo 5", role=None
            ),
            models.Application(
                name="Application 6", description="barfoo 6", role=None
            ),
        )
        for obj in applications:
            obj.save()

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
        role = models.ApplicationRole.objects.all()[:2]
        params = {"role_id": [role[0].pk, role[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"role": [role[0].slug, role[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
