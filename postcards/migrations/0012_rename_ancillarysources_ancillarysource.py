# Generated by Django 4.1.7 on 2023-10-19 19:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0011_ancillarysources"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AncillarySources",
            new_name="AncillarySource",
        ),
    ]
