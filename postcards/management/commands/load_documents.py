import logging
import os

import pandas as pd
from dateutil.parser import parse
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from taggit.models import Tag

from postcards.models import Collection, Image, Language, Person, PrimarySource

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
            item_id = row["item_number"]
            title = row["title"]
            document_type = str(row["type"]).lower()
            printer = row["printer"]
            date = row["date"]
            number_of_pages = row["number_of_pages"]
            translated = row["translated_(yes/no)"]
            medium = row["medium"]
            notes = row["notes"]
            date_of_indexing = row["date_entered"]
            keywords = row["keywords"]
            collection, _ = Collection.objects.get_or_create(
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

            # strip all whitespace from all data
            for key in row.keys():
                if isinstance(row[key], str):
                    row[key] = row[key].strip()

            DOC_TYPE_DICT = {
                "service record": "Service Record",
                "military record": "Military Record",
                "newspaper": "Newspaper",
                "certificate": "Certificate",
                "typed letter": "Typed Letter",
                "identification card": "Identification Card",
                "book": "Book",
                "loose pages": "Loose Pages",
                "photograph": "Photograph",
                "license": "License",
                "membership card": "Membership Card",
                "letter": "Letter",
                "letter/license": "Letter/License",
                "pay record": "Pay Record",
                "account balance": "Account Balance",
                "papers": "Papers",
                "discharge form": "Discharge Form",
                "pamphlet": "Pamphlet",
                "flyer": "Flyer",
                "program": "Program",
                "typewritten certificate": "Typewritten Certificate",
                "card": "Card",
                "identity card": "Identity Card",
                "booklet": "Booklet",
                "folded card": "Folded Card",
                "voucher": "Voucher",
                "pass": "Pass",
                "report": "Report",
                "stamps": "Stamps",
                "lettersheet": "Lettersheet",
                "other": "Other",
                'envelope ("printed matter")': 'Envelope ("printed matter")',
            }

            if document_type in DOC_TYPE_DICT:
                document_type = DOC_TYPE_DICT[document_type].lower()
                print(
                    f"Document Type '{document_type}' added to item {title} ({item_id})"
                )
            else:
                document_type = "other"

            try:
                primary_source = PrimarySource.objects.create(
                    item_id=item_id,
                    title=title,
                    document_type=document_type,
                    printer=printer,
                    date=date,
                    number_of_pages=number_of_pages,
                    has_document_been_translated=translated,
                    medium=medium,
                    notes=notes,
                    public_notes=notes,
                    date_cataloged=date_of_indexing,
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

            # After the objects exist, we then apply their tags
            try:
                document = PrimarySource.objects.get(item_id=item_id)
            except PrimarySource.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"No Object found with item_id {item_id}")
                )
                continue

            if pd.notnull(keywords):
                tags = [tag.strip() for tag in str(keywords).split(",")]
                for tag_name in tags:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    document.tags.add(tag)
                    document.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully added tag {tag_name} to object {item_id}."
                        )
                    )

            # Now we associate the images with the documents
            filepath = "static/upload"
            image_name = row["image"]
            # split the image_name at the comma and append .jpg
            filenames = image_name.split(",")
            filenames = [name.strip() for name in filenames]
            filenames = [name + ".jpg" for name in filenames]

            for filename in filenames:
                filename = os.path.basename(filename)
                full_path = os.path.join(filepath, filename)
                try:
                    with open(full_path, "rb") as f:
                        img = Image(primary_source=primary_source)
                        img.image.save(
                            filename, File(f)
                        )  # Save the image file to the Image instance
                        img.save()  # Save the Image instance
                        self.stdout.write(
                            self.style.SUCCESS(
                                "Successfully updated image for PrimarySource "
                            )
                            + self.style.WARNING(f"{item_id}")
                            + self.style.SUCCESS(" for image ")
                            + self.style.WARNING(f"{filename}")
                        )
                except FileNotFoundError:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Image {filename} does not exist for object {item_id}"
                        )
                    )
                except PrimarySource.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"PrimarySource {item_id} does not exist for image {filename}"
                        )
                    )
