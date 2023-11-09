# Generated by Django 4.1.7 on 2023-10-30 19:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0020_alter_object_date_of_correspondence"),
    ]

    operations = [
        migrations.AlterField(
            model_name="object",
            name="letter_enclosed",
            field=models.BooleanField(
                default=False,
                help_text="Check this box if there is a letter enclosed.",
                verbose_name="Letter enclosed",
            ),
        ),
    ]