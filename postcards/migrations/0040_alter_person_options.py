# Generated by Django 4.1.7 on 2023-12-05 14:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0039_remove_object_regime_censor_location_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="person",
            options={"ordering": ["last_name"], "verbose_name": "Entities or Person"},
        ),
    ]
