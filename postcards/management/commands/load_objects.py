import logging
import math
from datetime import datetime

import pandas as pd
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from taggit.models import Tag

from postcards.models import (
    Collection,
    Location,
    Object,
    Organization,
    Person,
    Postmark,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load data from an Excel file for the postal objects."

    def handle(self, *args, **options):
        file_path = "~/Downloads/arnhem.xlsx"
        try:
            with transaction.atomic():
                self.load_data(file_path)
                self.stdout.write(
                    self.style.SUCCESS("Objects data loaded successfully")
                )
        except Exception as e:
            logger.exception(f"Error loading Objects data: {str(e)}")
            self.stdout.write(
                self.style.ERROR("Error loading Objects data. Check logs for details.")
            )

    def load_data(self, file_path):
        try:
            df = pd.read_excel(file_path, sheet_name="Box 1 Folders I-VIII")

            for index, row in df.iterrows():
                try:
                    # Extract data from the row
                    entity_type = str(row["correspondence_type"]).lower()
                    item_number = str(row["Item Number"])
                    collection_location = str(row["Location in Collection"])
                    sensitive_content = str(row["Sensitive"]).lower() == "yes"
                    letter_enclosed = (
                        str(row["Letter Enclosed (yes/no)"]).lower() == "yes"
                    )
                    return_to_sender = str(row["Return to Sender"]).lower() == "yes"

                    date_of_correspondence = row["Date of Correspondence"]

                    # Check for NaT and 'NA' before converting to datetime
                    date_returned = row["Date Returned to sender"]
                    if pd.notna(date_returned) and date_returned not in ["NA", "No"]:
                        date_returned = pd.to_datetime(date_returned, errors="coerce")
                    else:
                        date_returned = None

                    date_of_correspondence = row["Date of Correspondence"]
                    if pd.notna(
                        date_of_correspondence
                    ) and date_of_correspondence not in ["NA", "No"]:
                        date_of_correspondence = pd.to_datetime(
                            date_of_correspondence, errors="coerce"
                        )
                    else:
                        date_of_correspondence = None

                    reason_for_return_original = str(
                        row["Reason for Return (Original language)"]
                    )
                    reason_for_return_translated = str(
                        row["Reason for Return (English)"]
                    )
                    # if reason_for_return_original or reason_for_return_translated includes the string "NA"
                    # then set the value to None
                    if "NA" in reason_for_return_original:
                        reason_for_return_original = None
                    if "NA" in reason_for_return_translated:
                        reason_for_return_translated = None

                    regime_censor = str(row["Censor"])

                    # Create or update Persons
                    addressee_first_name = str(row["Addressee First Name"])
                    addressee_last_name = str(row["Addressee Last Name"])
                    addressee = Person.objects.filter(
                        first_name=addressee_first_name,
                        last_name=addressee_last_name,
                    ).first()
                    if not addressee:
                        addressee = Person.objects.create(
                            entity_type=entity_type,
                            first_name=addressee_first_name,
                            last_name=addressee_last_name,
                        )

                    sender_first_name = str(row["Sender First Name"])
                    sender_last_name = str(row["Sender Last Name"])
                    sender = Person.objects.filter(
                        first_name=sender_first_name, last_name=sender_last_name
                    ).first()
                    if not sender:
                        sender = Person.objects.create(
                            entity_type=entity_type,
                            first_name=sender_first_name,
                            last_name=sender_last_name,
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
                        str(row["Type (Postcard/Letter/Package)"]).lower()
                    )

                    other_choices_mapping = {
                        "red cross": "Red Cross",
                        "uberroller": "uberroller",
                        "pow": "pow",
                    }
                    other = other_choices_mapping.get(
                        str(row["Other- RC, Uberroller, POW"]).lower()
                    )

                    public_notes = str(row["Notes"])
                    if pd.isna(public_notes) or public_notes.lower() == "nan":
                        public_notes = None

                    collection, _ = Collection.objects.get_or_create(
                        name="Tim Gale"
                    )  # Default to "Tim Gale"

                    # if correspondence_type == "person":
                    #     sender, _ = Person.objects.get_or_create(
                    #         first_name=sender_first_name,
                    #         last_name=sender_last_name,
                    #     )
                    #     addressee, _ = Person.objects.get_or_create(
                    #         first_name=addressee_first_name,
                    #         last_name=addressee_last_name,
                    #     )
                    # elif correspondence_type == "organization":
                    #     sender, _ = Organization.objects.get_or_create(
                    #         name=sender_first_name + " " + sender_last_name,
                    #         associated_with_person=None,
                    #     )
                    #     addressee, _ = Organization.objects.get_or_create(
                    #         name=addressee_first_name + " " + addressee_last_name,
                    #         associated_with_person=None,
                    #     )

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

                    try:
                        postmark_1_date = row["Postmark 1 Date"]
                        postmark_1_location_name = row["Postmark 1 Location"]
                        postmark_2_date = row["Postmark 2 Date"]
                        postmark_2_location_name = row["Postmark 2 Location"]

                        # Adjust finding the location
                        if postmark_1_location_name:
                            postmark_1_location = Location.objects.filter(
                                town_city=postmark_1_location_name
                            ).first()

                        if postmark_2_location_name:
                            postmark_2_location = Location.objects.filter(
                                town_city=postmark_2_location_name
                            ).first()

                        # Create or update postmarks and associate them with the object
                        if postmark_1_location:
                            postmark_1, _ = Postmark.objects.get_or_create(
                                date=postmark_1_date,
                                location=postmark_1_location,
                                ordered_by_arrival=1,
                            )
                        else:
                            # Handle the case when postmark_1_location is not found
                            postmark_1 = None

                        if postmark_2_date and postmark_2_location:
                            try:
                                # Convert the date string to a datetime object
                                if isinstance(postmark_2_date, str):
                                    postmark_2_date = datetime.strptime(
                                        postmark_2_date, "%Y-%m-%d"
                                    ).date()
                                elif isinstance(postmark_2_date, (float, int)):
                                    # Handle the case where postmark_2_date is a float or int
                                    if not math.isnan(postmark_2_date):
                                        postmark_2_date = datetime.fromordinal(
                                            datetime(1900, 1, 1).toordinal()
                                            + int(postmark_2_date)
                                            - 2
                                        ).date()
                                    else:
                                        postmark_2_date = None
                            except (ValueError, ValidationError) as e:
                                print(
                                    f"Error processing Postmark 2 Date '{postmark_2_date}': {e}"
                                )
                                postmark_2_date = None

                            # Create or update the Postmark object
                            postmark_2, _ = Postmark.objects.get_or_create(
                                date=postmark_2_date,
                                location=postmark_2_location,
                                ordered_by_arrival=2,
                            )

                            # Set the postmarks for the object
                            if postmark_1 or postmark_2:
                                obj.postmark.set(
                                    [pm for pm in [postmark_1, postmark_2] if pm]
                                )

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
