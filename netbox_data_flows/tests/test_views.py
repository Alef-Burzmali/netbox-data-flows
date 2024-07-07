from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse

from core.models import ObjectType
from extras.choices import ObjectChangeActionChoices
from extras.models import ObjectChange
from netbox.models.features import ChangeLoggingMixin
from users.models import ObjectPermission
from utilities.testing import (
    ViewTestCases,
    create_tags,
    post_data,
    disable_warnings,
)

from ipam import models as ipam

from netbox_data_flows import models, choices

from .data import TestData


class PluginUrlBase:
    def _get_base_url(self):
        base = super()._get_base_url()
        return "plugins:" + base

    def _get_url(self, action, instance=None, **kwargs):
        url_format = self._get_base_url()

        # If no instance was provided, assume we don't need a unique identifier
        if instance is None:
            return reverse(url_format.format(action), **kwargs)

        kwargs["pk"] = instance.pk
        return reverse(url_format.format(action), kwargs=kwargs)


class ApplicationRoleTestCase(
    PluginUrlBase, ViewTestCases.OrganizationalObjectViewTestCase
):
    model = models.ApplicationRole

    @classmethod
    def setUpTestData(cls):
        roles = TestData.create_applicationroles()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "Application Role X",
            "slug": "application-role-x",
            "description": "A new role",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,slug,description",
            "Application Role 4,application-role-4,Fourth application role",
            "Application Role 5,application-role-5,Fifth application role",
            "Application Role 6,application-role-6,Sixth application role",
        )

        cls.csv_update_data = (
            "id,name,description",
            f"{roles[0].pk},Application Role 7,Fourth role7",
            f"{roles[1].pk},Application Role 8,Fifth role8",
            f"{roles[2].pk},Application Role 0,Sixth role9",
        )

        cls.bulk_edit_data = {
            "description": "New description",
        }


class ApplicationTestCase(
    PluginUrlBase, ViewTestCases.PrimaryObjectViewTestCase
):
    model = models.Application

    @classmethod
    def setUpTestData(cls):
        roles = TestData.create_applicationroles()
        applications = TestData.create_applications()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        cls.form_data = {
            "name": "Application X",
            "description": "A new application",
            "role": roles[0].pk,
            "comments": "Some comments",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,description,role,comments",
            f"Application 7,Fourth application,{roles[0].slug},Comments 4",
            "Application 8,Fifth application,,Comments 5",
            f"Application 9,Sixth application,{roles[1].slug},",
        )

        cls.csv_update_data = (
            "id,name,description,comments",
            f"{applications[0].pk},Application 10,Fourth role7,Comments 7",
            f"{applications[1].pk},Application 11,Fifth role8,",
            f"{applications[2].pk},Application 12,Sixth role9,Comments 8",
        )

        cls.bulk_edit_data = {
            "description": "New description",
            "role": roles[2].pk,
            "comments": "New comments",
        }


class DataFlowGroupTestCase(
    PluginUrlBase, ViewTestCases.OrganizationalObjectViewTestCase
):
    model = models.DataFlowGroup

    @classmethod
    def setUpTestData(cls):
        apps = TestData.create_applications()
        groups = TestData.create_dataflowgroups()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        # parent must be a group with no parent
        # to avoid circular dependencies
        cls.form_data = {
            "name": "Data Flow Group X",
            "slug": "group-x",
            "description": "A new data flow group",
            "parent": groups[-1].pk,
            "application": apps[1].pk,
            "status": choices.DataFlowStatusChoices.STATUS_ENABLED,
            "comments": "Some comments",
            "tags": [t.pk for t in tags],
        }

        enabled = choices.DataFlowStatusChoices.STATUS_ENABLED
        disabled = choices.DataFlowStatusChoices.STATUS_DISABLED
        cls.csv_data = (
            "name,slug,description,parent,application,status,comments",
            f"Group 20,group-20,Fourth group,,{apps[0].name},{enabled},Comments 4",
            f"Group 21,group-21,Fifth group,{groups[3].slug},,{disabled},Comments 5",
            f"Group 22,group-22,Sixth,{groups[1].slug},{apps[1].name},{enabled},C 6",
        )

        cls.csv_update_data = (
            "id,name,description,parent,application,status,comments",
            f"{groups[0].pk},Group 30,Description 30,,,{disabled},Comments 7",
            f"{groups[1].pk},Group 31,,{groups[0].slug},{apps[1].name},{enabled},",
            f"{groups[2].pk},G 32,,{groups[0].slug},{apps[2].name},{disabled},C 8",
        )

        # cannot test parent: would assign itself
        cls.bulk_edit_data = {
            "description": "New description",
            "application": apps[0].pk,
            "status": disabled,
            "comments": "New comments",
        }

    def test_delete_object_with_constrained_permission(self):
        # Remove all parents to avoid deletion cascade that would
        # fail the test

        groups = models.DataFlowGroup.objects.all()
        for obj in groups:
            obj.parent = None
            obj.save()

        super().test_delete_object_with_constrained_permission()


class ObjectAliasTestCase(
    PluginUrlBase, ViewTestCases.PrimaryObjectViewTestCase
):
    model = models.ObjectAlias

    @classmethod
    def setUpTestData(cls):
        aliases = TestData.create_objectaliases()

        tags = create_tags("Alpha", "Bravo", "Charlie")

        # parent must be a group with no parent
        # to avoid circular dependencies
        cls.form_data = {
            "name": "Object Alias X",
            "description": "A new object alias",
            "comments": "Some comments",
            "tags": [t.pk for t in tags],
        }

        cls.csv_data = (
            "name,description,comments",
            "Alias 20,Fourth alias,Comments 4",
            "Alias 21,Fifth alias,",
            "Alias 22,Sixth description,Comments 6",
        )

        cls.csv_update_data = (
            "id,name,description,comments",
            f"{aliases[0].pk},Alias 30,Description 30,Comments 7",
            f"{aliases[1].pk},Alias 31,Description 31,",
            f"{aliases[2].pk},Alias 32,,Comments 8",
        )

        cls.bulk_edit_data = {
            "description": "New description",
            "comments": "New comments",
        }

        prefixes = ipam.Prefix.objects.all()[:2]
        ipranges = ipam.IPRange.objects.all()[:2]
        ipaddresses = ipam.IPAddress.objects.all()[:2]
        cls.addtarget_form_data = {
            "aliased_prefixes": [o.pk for o in prefixes],
            "aliased_ipranges": [o.pk for o in ipranges],
            "aliased_ipaddresses": [o.pk for o in ipaddresses],
        }

        cls.removetarget_form_data = {
            "confirm": "true",
        }

    def assertTargetsEqual(self, instance, data):
        forms_targets = []
        if data:
            forms_targets += list(
                ipam.Prefix.objects.filter(pk__in=data["aliased_prefixes"])
            )
            forms_targets += list(
                ipam.IPRange.objects.filter(pk__in=data["aliased_ipranges"])
            )
            forms_targets += list(
                ipam.IPAddress.objects.filter(
                    pk__in=data["aliased_ipaddresses"]
                )
            )

        expected_targets = []
        for expected_target_obj in forms_targets:
            expected_target = models.ObjectAliasTarget.get_or_create(
                expected_target_obj
            )
            self.assertTrue(
                expected_target.pk is not None,
                msg=(
                    f"Target {expected_target} ({expected_target_obj}) has "
                    "not been saved by the creation form"
                ),
            )
            expected_targets += [expected_target.pk]

        expected_targets = sorted(expected_targets)
        saved_targets = sorted([obj.pk for obj in instance.targets.all()])

        self.assertListEqual(expected_targets, saved_targets)

    def test_addtarget_without_permission(self):
        instance = self._get_queryset().first()

        # Try GET without permission
        with disable_warnings("django.request"):
            self.assertHttpStatus(
                self.client.get(self._get_url("addtarget", instance)), 403
            )

        # Try POST without permission
        request = {
            "path": self._get_url("addtarget", instance),
            "data": post_data(self.addtarget_form_data),
        }
        with disable_warnings("django.request"):
            self.assertHttpStatus(self.client.post(**request), 403)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"], EXEMPT_EXCLUDE_MODELS=[])
    def test_addtarget_with_permission(self):
        instance = models.ObjectAlias(
            name="Object Alias Addtarget A",
        )
        instance.save()

        # Assign model-level permission
        obj_perm = ObjectPermission(name="Test permission", actions=["change"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        self.assertHttpStatus(
            self.client.get(self._get_url("addtarget", instance)), 200
        )

        # Try POST with model-level permission
        request = {
            "path": self._get_url("addtarget", instance),
            "data": post_data(self.addtarget_form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)
        instance = self._get_queryset().get(pk=instance.pk)
        self.assertTargetsEqual(instance, self.addtarget_form_data)

        # Verify ObjectChange creation
        if issubclass(instance.__class__, ChangeLoggingMixin):
            objectchanges = ObjectChange.objects.filter(
                changed_object_type=ContentType.objects.get_for_model(
                    instance
                ),
                changed_object_id=instance.pk,
            )
            self.assertEqual(len(objectchanges), 1)
            self.assertEqual(
                objectchanges[0].action,
                ObjectChangeActionChoices.ACTION_UPDATE,
            )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"], EXEMPT_EXCLUDE_MODELS=[])
    def test_addtarget_with_constrained_permission(self):
        instance1 = models.ObjectAlias(
            name="Object Alias Addtarget B",
        )
        instance1.save()
        instance2 = models.ObjectAlias(
            name="Object Alias Addtarget C",
        )
        instance2.save()

        # Assign constrained permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance1.pk},
            actions=["change"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        # Try GET with a permitted object
        self.assertHttpStatus(
            self.client.get(self._get_url("addtarget", instance1)), 200
        )

        # Try GET with a non-permitted object
        self.assertHttpStatus(
            self.client.get(self._get_url("addtarget", instance2)), 404
        )

        # Try to edit a permitted object
        request = {
            "path": self._get_url("addtarget", instance1),
            "data": post_data(self.addtarget_form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)
        instance = self._get_queryset().get(pk=instance1.pk)
        self.assertTargetsEqual(instance, self.addtarget_form_data)

        # Try to edit a non-permitted object
        request = {
            "path": self._get_url("addtarget", instance2),
            "data": post_data(self.addtarget_form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 404)

    def test_removetarget_without_permission(self):
        instance = self._get_queryset().first()
        target = models.ObjectAliasTarget.objects.first()
        url = self._get_url("removetarget", instance, alias_pk=target.pk)

        # Try GET without permission
        with disable_warnings("django.request"):
            self.assertHttpStatus(self.client.get(url), 403)

        # Try POST without permission
        request = {
            "path": url,
            "data": post_data(self.removetarget_form_data),
        }
        with disable_warnings("django.request"):
            self.assertHttpStatus(self.client.post(**request), 403)

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"], EXEMPT_EXCLUDE_MODELS=[])
    def test_removetarget_with_permission(self):
        instance = models.ObjectAlias(
            name="Object Alias Addtarget A",
        )
        instance.save()
        target = models.ObjectAliasTarget.objects.first()
        instance.targets.set([target])

        url = self._get_url("removetarget", instance, alias_pk=target.pk)

        # Assign model-level permission
        obj_perm = ObjectPermission(name="Test permission", actions=["change"])
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        # Try GET with model-level permission
        self.assertHttpStatus(self.client.get(url), 200)

        # Try POST with model-level permission
        request = {
            "path": url,
            "data": post_data(self.removetarget_form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)
        instance = self._get_queryset().get(pk=instance.pk)
        self.assertTargetsEqual(instance, [])

        # Verify ObjectChange creation
        if issubclass(instance.__class__, ChangeLoggingMixin):
            objectchanges = ObjectChange.objects.filter(
                changed_object_type=ContentType.objects.get_for_model(
                    instance
                ),
                changed_object_id=instance.pk,
            )
            self.assertEqual(len(objectchanges), 1)
            self.assertEqual(
                objectchanges[0].action,
                ObjectChangeActionChoices.ACTION_UPDATE,
            )

    @override_settings(EXEMPT_VIEW_PERMISSIONS=["*"], EXEMPT_EXCLUDE_MODELS=[])
    def test_removetarget_with_constrained_permission(self):
        instance1 = models.ObjectAlias(
            name="Object Alias Addtarget B",
        )
        instance1.save()
        instance2 = models.ObjectAlias(
            name="Object Alias Addtarget C",
        )
        instance2.save()

        target = models.ObjectAliasTarget.objects.first()
        instance1.targets.set([target])
        target = models.ObjectAliasTarget.objects.first()
        instance2.targets.set([target])

        url1 = self._get_url("removetarget", instance1, alias_pk=target.pk)
        url2 = self._get_url("removetarget", instance2, alias_pk=target.pk)

        # Assign constrained permission
        obj_perm = ObjectPermission(
            name="Test permission",
            constraints={"pk": instance1.pk},
            actions=["change"],
        )
        obj_perm.save()
        obj_perm.users.add(self.user)
        obj_perm.object_types.add(ObjectType.objects.get_for_model(self.model))

        # Try GET with a permitted object
        self.assertHttpStatus(self.client.get(url1), 200)

        # Try GET with a non-permitted object
        self.assertHttpStatus(self.client.get(url2), 404)

        # Try to edit a permitted object
        request = {
            "path": url1,
            "data": post_data(self.removetarget_form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 302)
        instance = self._get_queryset().get(pk=instance1.pk)
        self.assertTargetsEqual(instance, [])

        # Try to edit a non-permitted object
        request = {
            "path": url2,
            "data": post_data(self.removetarget_form_data),
        }
        self.assertHttpStatus(self.client.post(**request), 404)
