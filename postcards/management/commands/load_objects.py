import logging
import math
from datetime import datetime

import pandas as pd
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
                self.stdout.write(
                    self.style.SUCCESS("Objects data loaded successfully")
                )
        except Exception as e:
            logger.exception(f"Error loading Objects data: {str(e)}")
            self.stdout.write(
                self.style.ERROR("Error loading Objects data. Check logs for details.")
            )

    def load_data(self, file_path, sheet_name=None):
        try:
            xls = pd.ExcelFile(file_path)
            dfs = {}

            if sheet_name:
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                df.columns = df.columns.str.strip()
                df.columns = df.columns.str.lower()
                dfs = {sheet_name: df}
            else:
                sheet_names = xls.sheet_names
                dfs = {}
                for sheet_name in sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                    df.columns = df.columns.str.strip()
                    df.columns = df.columns.str.lower()
                    dfs[sheet_name] = df

            for sheet_name, df in dfs.items():
                for index, row in df.iterrows():
                    try:
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
                            date_returned = pd.to_datetime(
                                date_returned, errors="coerce"
                            )
                        else:
                            date_returned = None

                        date_of_correspondence = row["date of correspondence"]
                        if pd.notna(
                            date_of_correspondence
                        ) and date_of_correspondence not in ["NA", "No"]:
                            date_of_correspondence = pd.to_datetime(
                                date_of_correspondence, errors="coerce"
                            )
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
                        addressee = Person.objects.filter(
                            first_name=addressee_first_name,
                            last_name=addressee_last_name,
                        ).first()
                        if not addressee:
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

                        sender_title = str(row["sender title"])
                        sender_first_name = str(row["sender first name"])
                        sender_last_name = str(row["sender last name"])
                        sender_house_number = str(row["sender house number"])
                        sender_street = str(row["sender street"])
                        sender_town_city = str(row["sender town/city"])
                        sender_province_state = str(row["sender province/state"])
                        sender_country = str(row["sender country"])
                        sender = Person.objects.filter(
                            first_name=sender_first_name, last_name=sender_last_name
                        ).first()
                        if not sender:
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

                        postmark_1_date = row["postmark 1 date"]
                        postmark_1_location_name = row["postmark 1 location"]
                        postmark_2_date = row["postmark 2 date"]
                        postmark_2_location_name = row["postmark 2 location"]

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

                        try:
                            # Create or update the postmarks
                            # Adjust finding the location
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
                                f"Initial postmark_1_date: {postmark_1_date} (type: {type(postmark_1_date)})"
                            )
                            # Create or update postmarks and associate them with the object
                            if postmark_1_location:
                                try:
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
                            else:
                                # Handle the case when postmark_1_location is not found
                                postmark_1 = None

                                # if postmark_2_location:
                                #     try:
                                #         # Convert the date string to a datetime object
                                #         if isinstance(postmark_2_date, str):
                                #             postmark_2_date = datetime.strptime(
                                #                 postmark_2_date, "%Y-%m-%d"
                                #             ).date()
                                #         elif isinstance(
                                #             postmark_2_date, (float, int)
                                #         ) and not math.isnan(postmark_2_date):
                                #             # Convert the float or int to a date
                                #             postmark_2_date = datetime.fromtimestamp(
                                #                 postmark_2_date
                                #             ).date()
                                #         else:
                                #             postmark_2_date = None
                                #     except (ValueError, ValidationError) as e:
                                #         print(
                                #             f"Error processing Postmark 2 Date '{postmark_2_date}': {e}"
                                #         )
                                #         postmark_2_date = None

                                #     # Create or update the Postmark object
                                #     postmark_2, _ = Postmark.objects.get_or_create(
                                #         date=postmark_2_date,
                                #         location=postmark_2_location,
                                #         ordered_by_arrival=2,
                                #     )

                                # print(f"postmark_1: {postmark_1}, postmark_2: {postmark_2}")

                                # Set the postmarks for the object
                                if postmark_1:
                                    obj.postmark.set([pm for pm in [postmark_1] if pm])

                        except Exception as e:
                            logger.exception(
                                f"Error processing postmarks for row {index + 2}: {str(e)}"
                            )
                            raise e

                    except Exception as e:
                        logger.exception(f"Error processing row {index + 2}: {str(e)}")
                        raise e

        except Exception as e:
            logger.exception(f"Error reading Excel file: {str(e)}")
            raise e
