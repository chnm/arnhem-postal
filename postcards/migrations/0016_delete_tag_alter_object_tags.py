# Generated by Django 4.1.7 on 2023-03-31 20:04

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("taggit", "0005_auto_20220424_2025"),
        ("postcards", "0015_remove_object_image_image_postcard"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Tag",
        ),
    ]