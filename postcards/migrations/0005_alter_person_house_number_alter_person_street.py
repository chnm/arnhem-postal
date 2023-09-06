# Generated by Django 4.1.7 on 2023-08-23 19:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0004_alter_person_first_name_alter_person_last_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="house_number",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="street",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]