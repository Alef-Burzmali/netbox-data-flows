# Generated by Django 5.0.6 on 2024-05-11 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("netbox_data_flows", "0010_alter_objectaliastarget_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="objectalias",
            name="comments",
            field=models.TextField(blank=True),
        ),
    ]