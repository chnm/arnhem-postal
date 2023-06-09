# Generated by Django 4.1.7 on 2023-03-23 19:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0002_rename_id_postcard_postcard_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2023, 3, 23, 19, 14, 57, 493306, tzinfo=datetime.timezone.utc
                ),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="location",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="person",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2023, 3, 23, 19, 15, 7, 984214, tzinfo=datetime.timezone.utc
                ),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="person",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="postcard",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2023, 3, 23, 19, 15, 13, 26046, tzinfo=datetime.timezone.utc
                ),
                verbose_name="date created",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="postcard",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="last updated"),
        ),
        migrations.AddField(
            model_name="tag",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2023, 3, 23, 19, 15, 19, 485461, tzinfo=datetime.timezone.utc
                ),
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tag",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
