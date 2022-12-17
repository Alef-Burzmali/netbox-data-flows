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
        )


class Migration(migrations.Migration):

    dependencies = [
        (
            "netbox_data_flows",
            "0003_alter_application_custom_field_data_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            code=reindex, reverse_code=migrations.RunPython.noop
        ),
    ]
