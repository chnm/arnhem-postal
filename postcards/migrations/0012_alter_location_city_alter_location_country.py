# Generated by Django 4.1.7 on 2023-03-24 14:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0011_postmark_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="city",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="location",
            name="country",
            field=models.CharField(max_length=100),
        ),
    ]
