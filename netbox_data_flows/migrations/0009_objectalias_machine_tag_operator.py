from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_data_flows", "0008_ltree_paths_conversion"),
    ]

    operations = [
        migrations.AddField(
            model_name="objectalias",
            name="machine_tag_operator",
            field=models.CharField(default="any", max_length=3),
        ),
    ]
