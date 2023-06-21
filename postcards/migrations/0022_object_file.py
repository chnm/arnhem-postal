# Generated by Django 4.1.7 on 2023-06-21 20:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0021_rename_collection_archive"),
    ]

    operations = [
        migrations.AddField(
            model_name="object",
            name="file",
            field=models.FileField(
                blank=True, null=True, upload_to="files/", verbose_name="Upload a file"
            ),
        ),
    ]