# Generated by Django 4.1.7 on 2023-12-05 18:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0042_alter_primarysource_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transcription",
            name="language",
        ),
        migrations.AddField(
            model_name="transcription",
            name="language",
            field=models.OneToOneField(
                blank=True,
                default=1,
                help_text="Select the language of this transcription",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="postcards.language",
            ),
        ),
    ]
