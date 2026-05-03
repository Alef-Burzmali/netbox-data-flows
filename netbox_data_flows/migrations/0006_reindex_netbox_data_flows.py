from django.db import migrations

# Transformed into no-op migration as NetBox upgrade script now
# runs the reindexation when required and after all migrations


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_data_flows", "0004_reindex_netbox_data_flows"),
        (
            "netbox_data_flows",
            "0005_dataflowgroup_slug",
        ),
    ]

    operations = []
