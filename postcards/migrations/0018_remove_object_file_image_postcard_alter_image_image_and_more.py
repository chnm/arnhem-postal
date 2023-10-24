# Generated by Django 4.1.7 on 2023-10-24 18:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0017_primarysource_item_id_primarysource_printer_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="object",
            name="file",
        ),
        migrations.AddField(
            model_name="image",
            name="postcard",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="images",
                to="postcards.object",
            ),
        ),
        migrations.AlterField(
            model_name="image",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="images/"),
        ),
        migrations.AlterField(
            model_name="image",
            name="image_caption",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
