# Generated by Django 4.1.7 on 2023-06-21 19:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "postcards",
            "0019_collection_object_letter_type_object_transcription_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="object",
            name="letter_type",
            field=models.CharField(
                choices=[
                    ("postcard", "Postcard"),
                    ("letter", "Letter"),
                    ("package", "Package"),
                    ("envolope", "Envelope"),
                ],
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="object",
            name="notes",
            field=models.TextField(
                blank=True,
                help_text="These notes are not visible to the public.",
                max_length=600,
                null=True,
                verbose_name="Internal notes",
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="title",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
