# Generated by Django 4.1.7 on 2023-12-05 16:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0041_remove_object_regime_censor_location_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="primarysource",
            options={"verbose_name": "Document"},
        ),
    ]
