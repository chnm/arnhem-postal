# Generated by Django 4.1.7 on 2023-12-05 20:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0044_alter_transcription_language"),
    ]

    operations = [
        migrations.AlterField(
            model_name="object",
            name="postmark",
            field=models.ManyToManyField(
                blank=True, null=True, to="postcards.postmark", verbose_name="postmark"
            ),
        ),
    ]
