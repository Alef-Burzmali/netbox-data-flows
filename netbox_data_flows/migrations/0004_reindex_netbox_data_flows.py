from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "netbox_data_flows",
            "0003_alter_application_custom_field_data_and_more",
        ),
    ]

    # noop to prevent two reindexing
    operations = []
