import logging

import pandas as pd
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from postcards.models import Collection, Language, Person, PrimarySource

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load data from an Excel file for the historical documents."

    def add_arguments(self, parser):
        parser.add_argument(
            "--filepath",
            type=str,
            help="filepath of excel file to load",
        )
        parser.add_argument(
            "--sheetname",
            type=str,
            help="name of sheet to load",
            default="Documents Database Ready",
        )

    def handle(self, *args, **options):
        file_path = options.get("filepath", None)
        sheet_name = options.get("sheetname", None)

        try:
            with transaction.atomic():
                self.load_data(file_path, sheet_name)
                self.stdout.write(self.style.SUCCESS("Successfully loaded data."))
        except Exception as e:
            logger.exception(f"Error loading Primary Source data: {str(e)}")
            self.stdout.write(
                self.style.ERROR(
                    "Error loading Primary Source data. Check logs for details."
                )
            )

    def load_data(self, file_path, sheet_name=None):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        # strip white space; lowercase columns names and replace spaces with underscores
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        for index, row in df.iterrows():
            # model fields are: item_id, document_type, person, printer, date, file, description, transcription, tags, notes, public_notes
            item_id = row["item_number"]
            title = row["title"]
            document_type = row["type"]
            printer = row["printer"]
            date = row["date"]
            number_of_pages = row["number_of_pages"]
            translated = row["translated_(yes/no)"]
            medium = row["medium"]
            notes = row["notes"]
            tags = row["keywords"]
            # cataloger = row["cataloger/indexer"]
            date_of_indexing = row["date_entered"]
            collection = Collection.objects.get_or_create(
                name="Tim Gale"
            )  # Default to "Tim Gale"
            collection_location = row["location"]

            # The "translated" field is a string of "No" or "Yes" in the Excel file.
            # We need to convert it to a boolean value.
            if translated == "Yes":
                translated = True
            elif translated == "No":
                translated = False
            else:
                translated = None

            try:
                primary_source = PrimarySource.objects.create(
                    item_id=item_id,
                    title=title,
                    document_type=document_type,
                    printer=printer,
                    date=date,
                    number_of_pages=number_of_pages,
                    translated=translated,
                    medium=medium,
                    notes=notes,
                    public_notes=notes,
                    tags=tags,
                    # cataloger=cataloger,
                    date_of_indexing=date_of_indexing,
                    collection=collection,
                    collection_location=collection_location,
                )
            except PrimarySource.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"No historical document found with item_id {item_id}"
                    )
                )
                continue
