# Generated by Django 4.1.7 on 2023-08-23 18:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0003_alter_person_date_of_birth_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="person",
            name="first_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="person",
            name="last_name",
            field=models.CharField(max_length=255),
        ),
    ]
