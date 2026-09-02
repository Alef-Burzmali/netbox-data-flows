"""Replace django-mptt with PostgreSQL ltree for tenancy's hierarchical models.

For each model this migration:

1. Enables the PostgreSQL ltree extension (idempotent).
2. Adds a nullable `path` LTreeField. For models that previously had
   `MPTTMeta.order_insertion_by = ('name',)`, also adds a `sort_path` text column.
3. Installs per-table BEFORE/AFTER triggers. For models with sort_path, the
   trigger maintains both columns.
4. Populates path (and sort_path where applicable) for existing rows via a
   single recursive CTE per table.
5. Tightens path to NOT NULL.
6. Drops the legacy MPTT columns (lft, rght, tree_id, level).
7. Adds a GiST index on path (descendant/ancestor lookups via `<@` / `@>`).
   For sort_path models, also adds a btree index for ORDER BY listing.

The reverse migration is lossy: it re-adds the MPTT columns empty and does not
rebuild the tree. Forward migration is the supported direction.

Copied from netbox/tenancy/migrations/0025_ltree_paths.py @v4.7.0
"""

import django.contrib.postgres.indexes
import django.contrib.postgres.operations
import django.db.models.deletion
from django.db import migrations, models

import netbox.models.ltree
from utilities.ltree import InstallLtreeTriggers
from utilities.mptt_to_ltree import assert_paths_populated_sql, populate_paths_sql

MODELS = ("dataflowgroup",)
TABLES = ("netbox_data_flows_dataflowgroup",)
LEGACY_FIELDS = ("lft", "rght", "tree_id", "level")


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0144_customfield_status"),
        ("netbox_data_flows", "0007_objectalias_tagged_members"),
        ("tenancy", "0026_consolidate_unique_constraints"),
        ("users", "0016_default_ordering_indexes"),
    ]

    operations = [
        # Enable the ltree extension first so the migration fails fast if it is missing.
        django.contrib.postgres.operations.CreateExtension("ltree"),
        # Switch parent from mptt.fields.TreeForeignKey to django.db.models.ForeignKey.
        migrations.AlterField(
            model_name="dataflowgroup",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="netbox_data_flows.dataflowgroup",
            ),
        ),
        # Add path (nullable initially) on model.
        *[
            migrations.AddField(
                model_name=m,
                name="path",
                field=netbox.models.ltree.LtreeField(blank=True, editable=False, null=True),
            )
            for m in MODELS
        ],
        # Add sort_path.
        *[
            migrations.AddField(
                model_name=m,
                name="sort_path",
                field=models.TextField(blank=True, default="", editable=False),
            )
            for m in MODELS
        ],
        # Install triggers maintaining both path and sort_path.
        *[InstallLtreeTriggers(t, name_column="name") for t in TABLES],
        # Populate path and sort_path for existing rows via per-table recursive CTE.
        migrations.RunSQL(
            "\n".join(populate_paths_sql(t, sort_path=True) for t in TABLES),
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Fail fast if any row still has NULL path (orphan FKs) before the
        # AlterField below tries to set NOT NULL inside ALTER COLUMN.
        migrations.RunSQL(
            "\n".join(assert_paths_populated_sql(t) for t in TABLES),
            reverse_sql=migrations.RunSQL.noop,
        ),
        *[
            migrations.AlterField(
                model_name=m,
                name="path",
                field=netbox.models.ltree.LtreeField(blank=True, default="", editable=False),
            )
            for m in MODELS
        ],
        migrations.AlterModelOptions(
            name="dataflowgroup",
            options={"ordering": ("sort_path",)},
        ),
        # Drop legacy (tree_id, lft) indexes and the MPTT columns.
        # migrations.RemoveIndex(model_name="dataflowgroup", name="netbox_data_flows_dataflowgroup_tree_id_faa41f90"),
        *[migrations.RemoveField(model_name=m, name=f) for m in MODELS for f in LEGACY_FIELDS],
        # GiST indexes on path.
        migrations.AddIndex(
            model_name="dataflowgroup",
            index=django.contrib.postgres.indexes.GistIndex(fields=["path"], name="netbox_data_flows_dfg_path_gist"),
        ),
        # Btree indexes on sort_path for ORDER BY listing.
        migrations.AddIndex(
            model_name="dataflowgroup",
            index=models.Index(fields=["sort_path"], name="netbox_data_flows_dfg_spath_ix"),
        ),
    ]
