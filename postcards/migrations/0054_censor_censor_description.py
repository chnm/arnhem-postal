# Generated by Django 4.1.7 on 2024-01-26 16:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0053_object_reviewed_by_date_alter_object_reviewed_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="censor",
            name="censor_description",
            field=models.CharField(
                blank=True,
                help_text="A brief description of the censor if needed.",
                max_length=255,
                null=True,
            ),
        ),
    ]
