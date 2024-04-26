import logging

import pandas as pd
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from postcards.models import Language, Object, Transcription

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load data from an Excel file for the transcriptions."

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
        # strip white space; lowercase columns names and replace spaces with underscores
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        for index, row in df.iterrows():
            item_id = row["item_number"]
            transcription = row["transcription"]
            translation = row["translation"]

            try:
                postal_object = Object.objects.filter(item_id=item_id)
            except Object.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"No Object found with item_id {item_id}")
                )
                continue

            # If there's a transcription and it's not 'nan', we default to German as the language and insert the transcription
            if pd.notna(transcription) and transcription != "nan":
                try:
                    german_language = Language.objects.get(language="German")
                    for mail in postal_object:
                        Transcription.manager.create(
                            postal_object=mail,
                            transcription=transcription,
                            language=german_language,
                        )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"German Transcription for Object {item_id} created successfully"
                        )
                    )
                except ValidationError as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error creating German Transcription for Object {item_id}: {str(e)}"
                        )
                    )

            # If there's a translation and it's not 'nan', we set the language to English and insert the data into the transcription from the translation column
            if pd.notna(translation) and translation != "nan":
                try:
                    english_language = Language.objects.get(language="English")
                    for mail in postal_object:
                        Transcription.manager.create(
                            postal_object=mail,
                            transcription=translation,
                            language=english_language,
                        )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"English Transcription for Object {item_id} created successfully"
                        )
                    )
                except ValidationError as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error creating English Transcription for Object {item_id}: {str(e)}"
                        )
                    )
