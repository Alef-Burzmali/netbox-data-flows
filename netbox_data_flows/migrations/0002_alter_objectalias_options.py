# Generated by Django 4.0.8 on 2022-11-30 14:04

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_data_flows", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="objectalias",
            options={
                "ordering": ("name",),
                "verbose_name_plural": "Object Aliases",
            },
        ),
    ]
