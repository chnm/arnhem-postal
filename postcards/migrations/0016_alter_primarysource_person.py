# Generated by Django 4.1.7 on 2023-10-19 22:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0015_primarysource_related_postal_items_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="primarysource",
            name="person",
            field=models.ManyToManyField(
                blank=True,
                help_text="Select the person this document is about. If the person does not exist, click the plus and add the new person.",
                related_name="person",
                to="postcards.person",
                verbose_name="person",
            ),
        ),
    ]
