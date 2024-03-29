# Generated by Django 4.1.7 on 2023-11-09 19:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0033_postmark_ordered_by_arrival"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="first_name_unknown",
            field=models.BooleanField(
                default=False,
                help_text="Check this box if the first name is unknown.",
                verbose_name="First name unknown",
            ),
        ),
        migrations.AddField(
            model_name="person",
            name="last_name_unknown",
            field=models.BooleanField(
                default=False,
                help_text="Check this box if the last name is unknown.",
                verbose_name="Last name unknown",
            ),
        ),
        migrations.CreateModel(
            name="Organization",
            fields=[
                (
                    "org_id",
                    models.BigAutoField(
                        primary_key=True,
                        serialize=False,
                        verbose_name="Organization ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="postcards.location",
                    ),
                ),
            ],
        ),
    ]
