# Generated by Django 4.1.7 on 2023-03-23 20:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0009_remove_location_name_remove_postmark_date_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="postmark",
            name="latitude",
        ),
        migrations.RemoveField(
            model_name="postmark",
            name="longitude",
        ),
    ]
