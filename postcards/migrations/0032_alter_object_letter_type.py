# Generated by Django 4.1.7 on 2023-11-09 17:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0031_remove_object_collection_object_collection"),
    ]

    operations = [
        migrations.AlterField(
            model_name="object",
            name="letter_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("postcard", "Postcard"),
                    ("letter", "Letter"),
                    ("package", "Package"),
                    ("envelope", "Envelope"),
                    ("folded card", "Folded Card"),
                    ("envelope printed matter", "Envelope ('printed matter')"),
                    ("letter sheet", "Letter Sheet"),
                    ("giro envelope", "Giro Envelope"),
                    ('envelope ("printed matter")', 'Envelope ("printed matter")'),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
