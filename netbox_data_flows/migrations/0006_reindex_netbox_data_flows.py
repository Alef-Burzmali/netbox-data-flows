import sys

from django.core import management
from django.db import migrations


def reindex(apps, schema_editor):
    # Build the search index (except during tests)
    if "test" not in sys.argv:
        management.call_command(
            "reindex",
            "netbox_data_flows.Application",
            "netbox_data_flows.ApplicationRole",
            "netbox_data_flows.DataFlow",
            "netbox_data_flows.DataFlowGroup",
            "netbox_data_flows.ObjectAlias",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_data_flows", "0004_reindex_netbox_data_flows"),
        (
            "netbox_data_flows",
            "0005_dataflowgroup_slug",
        ),
    ]

    operations = [
        migrations.RunPython(
            code=reindex, reverse_code=migrations.RunPython.noop
        ),
    ]
