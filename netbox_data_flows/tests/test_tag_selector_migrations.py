from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class TagSelectorMigrationTestCase(TransactionTestCase):
    def test_existing_alias_keeps_its_selectors(self):
        executor = MigrationExecutor(connection)
        current = executor.loader.graph.leaf_nodes()
        previous = [("netbox_data_flows", "0008_ltree_paths_conversion")]
        try:
            executor.migrate(previous)
            apps = executor.loader.project_state(previous).apps
            alias = apps.get_model("netbox_data_flows", "ObjectAlias").objects.create(
                name="migration-alias", tag_matching_rule="all"
            )
            tag = apps.get_model("extras", "Tag").objects.create(name="migration-tag", slug="migration-tag")
            alias.device_tags.through.objects.create(objectalias_id=alias.pk, tag_id=tag.pk)
            alias.virtual_machine_tags.through.objects.create(objectalias_id=alias.pk, tag_id=tag.pk)
        finally:
            MigrationExecutor(connection).migrate(current)

        apps = MigrationExecutor(connection).loader.project_state(current).apps
        migrated = apps.get_model("netbox_data_flows", "ObjectAlias").objects.get(pk=alias.pk)
        self.assertEqual(migrated.machine_tag_operator, "any")
        self.assertEqual(migrated.tag_matching_rule, "all")
        self.assertEqual(list(migrated.device_tags.values_list("pk", flat=True)), [tag.pk])
        self.assertEqual(list(migrated.virtual_machine_tags.values_list("pk", flat=True)), [tag.pk])
