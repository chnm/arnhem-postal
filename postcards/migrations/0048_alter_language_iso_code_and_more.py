# Generated by Django 4.1.7 on 2023-12-11 16:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("postcards", "0047_person_first_name_unclear_person_last_name_unclear"),
    ]

    operations = [
        migrations.AlterField(
            model_name="language",
            name="iso_code",
            field=models.CharField(
                blank=True,
                help_text="ISO 639 code for this language (2 or 3 letters)",
                max_length=3,
            ),
        ),
        migrations.AlterField(
            model_name="object",
            name="reason_for_return_original",
            field=models.TextField(
                blank=True,
                help_text="The reason for return in the original language.",
                max_length=600,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="object",
            name="reason_for_return_translated",
            field=models.TextField(
                blank=True,
                help_text="The reason for return translated to English.",
                max_length=600,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="first_name_unclear",
            field=models.BooleanField(
                default=False,
                help_text="Check this box if the first name is unclear or illegible.",
                verbose_name="First name unclear",
            ),
        ),
        migrations.AlterField(
            model_name="person",
            name="last_name_unclear",
            field=models.BooleanField(
                default=False,
                help_text="Check this box if the last name is unclear or illegible.",
                verbose_name="Last name unclear",
            ),
        ),
    ]
