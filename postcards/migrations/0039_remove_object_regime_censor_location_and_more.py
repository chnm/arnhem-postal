# Generated by Django 4.1.7 on 2023-12-05 01:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0038_alter_person_options_delete_organization"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="object",
            name="regime_censor_location",
        ),
        migrations.AddField(
            model_name="object",
            name="regime_censor_location",
            field=models.ForeignKey(
                blank=True,
                help_text="Select the location of the censor. If the location does not exist, click the plus and add the new location.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="postcards.location",
            ),
        ),
    ]
