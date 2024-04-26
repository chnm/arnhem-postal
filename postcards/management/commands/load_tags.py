import logging

import pandas as pd
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from taggit.models import Tag

from postcards.models import Object

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load data from an Excel file for the postal objects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--filepath", type=str, help="filepath of excel file to load"
        )
        parser.add_argument("--sheetname", type=str, help="name of sheet to load")

    def handle(self, *args, **options):
        file_path = options.get("filepath", None)
        sheet_name = options.get("sheetname", None)

        try:
            with transaction.atomic():
                self.load_data(file_path, sheet_name)
                self.stdout.write(self.style.SUCCESS("Successfully loaded data."))
        except Exception as e:
            logger.exception(f"Error loading Objects data: {str(e)}")
            self.stdout.write(
                self.style.ERROR("Error loading Objects data. Check logs for details.")
            )

    def load_data(self, file_path, sheet_name=None):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        for index, row in df.iterrows():
            item_id = row["item_number"]
            keywords = row["key_words"]

            try:
                document = Object.objects.filter(item_id=item_id)
            except Object.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"No Object found with item_id {item_id}")
                )
                continue

            if pd.notnull(keywords):
                tags = [tag.strip() for tag in str(keywords).split(",")]
                for tag_name in tags:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    for doc in document:
                        doc.tags.add(tag)
                        doc.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully added tag {tag_name} to object {item_id}."
                        )
                    )
