import logging
import math
from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.parser import parse
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from postcards.models import (
    Collection,
    Language,
    Location,
    Object,
    Person,
    Postmark,
    Transcription,
)

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
        try:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Loading data from file {file_path} and sheet {sheet_name}"
                )
            )
            xls = pd.ExcelFile(file_path)
            dfs = {}

            if sheet_name:
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                df = df.replace({np.nan: None})
                df.columns = df.columns.str.strip()
                df.columns = df.columns.str.lower()
                dfs = {sheet_name: df}
            else:
                sheet_names = xls.sheet_names
                dfs = {}
                for sheet_name in sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                    df = df.replace({np.nan: None})
                    df.columns = df.columns.str.strip()
                    df.columns = df.columns.str.lower()
                    dfs[sheet_name] = df

            for sheet_name, df in dfs.items():
                for index, row in df.iterrows():
                    try:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Processing row {index + 2} of sheet {sheet_name}"
                            )
                        )

                        # Extract data from the row
                        entity_type = str(
                            row.get("correspondence_type") or "Person"
                        ).lower()
                        item_number = str(row["item number"])
                        collection_location = str(row["location in collection"])
                        sensitive_content = str(row["sensitive"]).lower() == "yes"
                        letter_enclosed = (
                            str(row["letter enclosed (yes/no)"]).lower() == "yes"
                        )
                        return_to_sender = str(row["return to sender"]).lower() == "yes"

                        date_of_correspondence = row["date of correspondence"]

                        # Check for NaT and 'NA' before converting to datetime
                        date_returned = row["date returned to sender"]
                        if pd.notna(date_returned) and date_returned not in [
                            "NA",
                            "No",
                        ]:
                            try:
                                date_returned = pd.to_datetime(
                                    date_returned, errors="coerce"
                                )
                            except (ValueError, TypeError):
                                date_returned = None
                        else:
                            date_returned = None

                        date_of_correspondence = row["date of correspondence"]
                        if pd.notna(
                            date_of_correspondence
                        ) and date_of_correspondence not in ["NA", "No"]:
                            try:
                                date_of_correspondence = pd.to_datetime(
                                    date_of_correspondence, errors="coerce"
                                )
                            except (ValueError, TypeError):
                                date_of_correspondence = None
                        else:
                            date_of_correspondence = None

                        reason_for_return_original = str(
                            row["reason for return (original language)"]
                        )
                        reason_for_return_translated = str(
                            row["reason for return (english)"]
                        )
                        # if reason_for_return_original or reason_for_return_translated includes the string "NA"
                        # then set the value to None
                        if "NA" in reason_for_return_original:
                            reason_for_return_original = None
                        if "NA" in reason_for_return_translated:
                            reason_for_return_translated = None

                        regime_censor = str(row["censor"])

                        transcription_original = str(row["transcription"])
                        transcription_english = str(row["translation"])

                        # Create or update Persons
                        addressee_title = str(row["addressee title"])
                        addressee_first_name = str(row["addressee first name"])
                        addressee_last_name = str(row["addressee last name"])
                        addressee_house_number = str(row["addressee house number"])
                        addressee_street = str(row["addressee street"])
                        addressee_town_city = str(row["addressee town/city"])
                        addressee_province_state = str(row["addressee province/state"])
                        addressee_country = str(row["addressee country"])

                        sender_title = str(row["sender title"])
                        sender_first_name = str(row["sender first name"])
                        sender_last_name = str(row["sender last name"])
                        sender_house_number = str(row["sender house number"])
                        sender_street = str(row["sender street"])
                        sender_town_city = str(row["sender town/city"])
                        sender_province_state = str(row["sender province/state"])
                        sender_country = str(row["sender country"])

                        postmark_1_date = row["postmark 1 date"]
                        postmark_1_location_name = row["postmark 1 location"]
                        postmark_2_date = row["postmark 2 date"]
                        postmark_2_location_name = row["postmark 2 location"]

                        # Now, we create the Location data in the model. This data comes from
                        # the following fields:
                        # addressee_province_state = str(row["addressee province/state"])
                        # addressee_country = str(row["addressee country"])
                        # sender_province_state = str(row["sender province/state"])
                        # sender_country = str(row["sender country"])
                        # postmark_1_location_name = row["postmark 1 location"]
                        # postmark_2_location_name = row["postmark 2 location"]
                        # From these fields, we can create the Location data. We need to
                        # check if the Location already exists. If it does, we use that
                        # Location. If it doesn't, we create a new Location.

                        addressee_location = Location.objects.filter(
                            town_city=addressee_town_city,
                            province_state=addressee_province_state,
                            country=addressee_country,
                        ).first()

                        sender_location = Location.objects.filter(
                            town_city=sender_town_city,
                            province_state=sender_province_state,
                            country=sender_country,
                        ).first()

                        # print the postmark being processed
                        self.stdout.write(
                            self.style.NOTICE(
                                f"Processing POSTMARK 1 LOCATION ${postmark_1_location_name} for row {index + 2} of sheet {sheet_name}"
                            )
                        )

                        postmark_1_location = Location.objects.filter(
                            town_city=postmark_1_location_name
                        ).first()

                        if postmark_1_location_name is not None:
                            postmark_1_location = Location.objects.filter(
                                town_city=postmark_2_location_name
                            ).first()
                        else:
                            postmark_1_location = None

                        # print the postmark being processed
                        self.stdout.write(
                            self.style.NOTICE(
                                f"Processing POSTMARK 2 LOCATION ${postmark_2_location_name} for row {index + 2} of sheet {sheet_name}"
                            )
                        )

                        if postmark_2_location_name is not None:
                            postmark_2_location = Location.objects.filter(
                                town_city=postmark_2_location_name
                            ).first()
                        else:
                            postmark_2_location = None

                        addressee = Person.objects.filter(
                            first_name=addressee_first_name,
                            last_name=addressee_last_name,
                        ).first()
                        if not addressee:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Creating addressee {addressee_first_name} {addressee_last_name}"
                                )
                            )
                            addressee = Person.objects.create(
                                entity_type=entity_type,
                                title=addressee_title,
                                first_name=addressee_first_name,
                                last_name=addressee_last_name,
                                house_number=addressee_house_number,
                                street=addressee_street,
                                location=Location.objects.filter(
                                    town_city=addressee_town_city,
                                    province_state=addressee_province_state,
                                    country=addressee_country,
                                ).first(),
                            )

                        sender = Person.objects.filter(
                            first_name=sender_first_name, last_name=sender_last_name
                        ).first()
                        if not sender:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Creating sender {sender_first_name} {sender_last_name}"
                                )
                            )
                            sender = Person.objects.create(
                                entity_type=entity_type,
                                title=sender_title,
                                first_name=sender_first_name,
                                last_name=sender_last_name,
                                house_number=sender_house_number,
                                street=sender_street,
                                location=Location.objects.filter(
                                    town_city=sender_town_city,
                                    province_state=sender_province_state,
                                    country=sender_country,
                                ).first(),
                            )

                        letter_type_mapping = {
                            "postcard": "Postcard",
                            "letter": "Letter",
                            "package": "Package",
                            "envelope": "Envelope",
                            "folded card": "Folded Card",
                            "envelope printed matter": 'Envelope ("printed matter")',
                            "letter sheet": "Letter Sheet",
                            "giro envelope": "Giro Envelope",
                            'envelope ("printed matter")': 'Envelope ("printed matter")',
                        }
                        letter_type = letter_type_mapping.get(
                            str(row["type (postcard/letter/package)"]).lower()
                        )

                        other_choices_mapping = {
                            "red cross": "Red Cross",
                            "uberroller": "uberroller",
                            "pow": "pow",
                        }
                        other = other_choices_mapping.get(
                            str(row["other- rc, uberroller, pow"]).lower()
                        )

                        public_notes = str(row["notes"])
                        if pd.isna(public_notes) or public_notes.lower() == "nan":
                            public_notes = None

                        collection, _ = Collection.objects.get_or_create(
                            name="Tim Gale"
                        )  # Default to "Tim Gale"

                        # Before we write the data to the obj, we replace the None
                        # values with empty strings. This is done throughout all of the
                        # data. So, we find any instance where the value is None and
                        # replace it with an empty string.
                        # for key, value in row.items():
                        #     if value is None:
                        #         row[key] = ""

                        # Create or update Objects instance
                        obj, _ = Object.objects.get_or_create(
                            item_id=item_number,
                            collection=collection,
                            collection_location=collection_location,
                            check_sensitive_content=sensitive_content,
                            letter_enclosed=letter_enclosed,
                            return_to_sender=return_to_sender,
                            date_returned=date_returned,
                            reason_for_return_original=reason_for_return_original,
                            reason_for_return_translated=reason_for_return_translated,
                            regime_censor=regime_censor,
                            addressee_name=addressee,
                            sender_name=sender,
                            letter_type=letter_type,
                            date_of_correspondence=date_of_correspondence,
                            other=other,
                            public_notes=public_notes,
                        )

                        if transcription_original:
                            language = Language.objects.get(language="Dutch")
                            transcription_text = transcription_original
                        else:
                            language = Language.objects.get(language="English")
                            transcription_text = transcription_english

                        transcription, created = Transcription.manager.update_or_create(
                            postal_object=obj,
                            transcription=transcription_text,
                            language=language,
                        )

                        # Create or update postmarks
                        # Set the initial values to None
                        # postmark_1_location = None
                        # postmark_2_location = None

                        try:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Processing postmarks for row {index + 2} of sheet {sheet_name}"
                                )
                            )
                            # Create or update the postmarks
                            if postmark_1_location_name:
                                postmark_1_location = (
                                    Location.objects.filter(
                                        town_city=postmark_1_location_name
                                    ).first()
                                    if postmark_1_location_name
                                    else None
                                )

                            if postmark_2_location_name:
                                postmark_2_location = (
                                    Location.objects.filter(
                                        town_city=postmark_2_location_name
                                    ).first()
                                    if postmark_2_location_name
                                    else None
                                )

                            print(
                                f"Initial postmark_1_date: {postmark_1_date} (type: {type(postmark_1_date)})",
                                f"Initial postmark_1_location: {postmark_1_location} (type: {type(postmark_1_location)})",
                                f"Initial postmark_2_date: {postmark_2_date} (type: {type(postmark_2_date)})",
                                f"Initial postmark_2_location: {postmark_2_location} (type: {type(postmark_2_location)})",
                            )
                            # Create or update postmarks and associate them with the object
                            if postmark_1_location:
                                try:
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f"Processing Postmark 1 for row {index + 2} of sheet {sheet_name}"
                                        )
                                    )
                                    # Convert the date string to a datetime object
                                    if isinstance(postmark_1_date, str):
                                        postmark_1_date = datetime.strptime(
                                            postmark_1_date, "%Y-%m-%d %H:%M:%S"
                                        ).date()
                                    elif isinstance(
                                        postmark_1_date, (float, int)
                                    ) and not math.isnan(postmark_1_date):
                                        # Convert the float or int to a date
                                        postmark_1_date = datetime.fromtimestamp(
                                            postmark_1_date
                                        ).date()
                                    else:
                                        postmark_1_date = None
                                except (ValueError, ValidationError) as e:
                                    print(
                                        f"Error processing Postmark 1 Date '{postmark_1_date}': {e}"
                                    )
                                    postmark_1_date = None

                                print(
                                    f"Final postmark_1_date: {postmark_1_date} (type: {type(postmark_1_date)})"
                                )
                                postmark_1, _ = Postmark.objects.get_or_create(
                                    date=postmark_1_date,
                                    location=postmark_1_location,
                                    ordered_by_arrival=1,
                                )

                            if postmark_2_location:
                                try:
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f"Processing Postmark 2 for row {index + 2} of sheet {sheet_name}"
                                        )
                                    )
                                    # Convert the date string to a datetime object
                                    if isinstance(postmark_2_date, str):
                                        postmark_2_date = datetime.strptime(
                                            postmark_2_date, "%Y-%m-%d %H:%M:%S"
                                        ).date()
                                    elif isinstance(
                                        postmark_2_date, (float, int)
                                    ) and not math.isnan(postmark_2_date):
                                        # Convert the float or int to a date
                                        postmark_2_date = datetime.fromtimestamp(
                                            postmark_2_date
                                        ).date()
                                    else:
                                        postmark_2_date = None
                                except (ValueError, ValidationError) as e:
                                    print(
                                        f"Error processing Postmark 2 Date '{postmark_2_date}': {e}"
                                    )
                                    postmark_2_date = None

                                print(
                                    f"Final postmark_2_date: {postmark_2_date} (type: {type(postmark_2_date)})"
                                )
                                postmark_2, _ = Postmark.objects.get_or_create(
                                    date=postmark_2_date,
                                    location=postmark_2_location,
                                    ordered_by_arrival=2,
                                )

                            # Now that the postmarks exist, we can associate them with
                            # the postal object. We need to do this after the postmarks
                            # are created because the postmark needs to exist before
                            # we can associate it with the postal object.
                            try:
                                # we look up the postmark by date and location
                                if postmark_1_location:
                                    postmark_1 = Postmark.objects.get(
                                        date=postmark_1_date,
                                        location=postmark_1_location,
                                    )
                                    obj.postmark.add(postmark_1)

                                if postmark_2_location:
                                    postmark_2 = Postmark.objects.get(
                                        date=postmark_2_date,
                                        location=postmark_2_location,
                                    )
                                    obj.postmark.add(postmark_2)

                            except Postmark.DoesNotExist as e:
                                print(
                                    f"Error associating postmark with postal object: {e}"
                                )
                                raise e

                        except Exception as e:
                            logger.exception(
                                "Error processing postmarks for row %s: %s",
                                index + 2,
                                str(e),
                            )
                            raise e

                    except Exception as e:
                        logger.exception(
                            "Error processing row %s: %s", index + 2, str(e)
                        )
                        raise e

        except Exception as e:
            logger.exception("Error reading Excel file: %s", str(e))
            raise e
