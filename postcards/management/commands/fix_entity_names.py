import logging
import math
from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.parser import parse
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from postcards.models import Person

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
            logger.exception(f"Error updating People data: {str(e)}")
            self.stdout.write(
                self.style.ERROR("Error loading People data. Check logs for details.")
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

                        # Get the sender's first_name and last_name
                        sender_first_name = str(row["sender first name"])
                        sender_last_name = str(row["sender last name"])
                        sender_entity_name = str(row["entitiy"])
                        sender_entity_type = str(row["sender correspondence type"])

                        # If both first_name and last_name are None, but entity_name exists, create a new Person object
                        if (
                            sender_first_name == "None"
                            and sender_last_name == "None"
                            and sender_entity_name
                        ):
                            sender = Person.objects.create(
                                entity_name=sender_entity_name,
                                entity_type=sender_entity_type,
                            )
                        # If either first_name or last_name exists, try to get the Person object
                        elif sender_first_name != "None" or sender_last_name != "None":
                            sender = Person.objects.filter(
                                first_name=sender_first_name, last_name=sender_last_name
                            ).first()

                        # If there is no Person object and entity_name exists, create a new Person object
                        if not sender and sender_entity_name:
                            sender = Person.objects.create(
                                first_name=sender_first_name
                                if sender_first_name != "None"
                                else None,
                                last_name=sender_last_name
                                if sender_last_name != "None"
                                else None,
                                entity_name=sender_entity_name,
                                entity_type=sender_entity_type,
                            )
                        # If there is a Person object, update the entity_name and entity_type
                        elif sender:
                            sender.entity_name = sender_entity_name
                            sender.entity_type = sender_entity_type
                            sender.save()

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"|- Updated sender entity name for person {sender_first_name} {sender_last_name} ({sender})"
                                    f"\n|-- {sender_entity_name} - {sender_entity_type}"
                                )
                            )

                        # Get the addressee's first_name and last_name
                        addressee_first_name = str(row["addressee first name"])
                        addressee_last_name = str(row["addressee last name"])
                        addressee_entity_name = str(row["addressee entity"])
                        addressee_entity_type = str(row["addresse correspondence type"])

                        # If both first_name and last_name are None, but entity_name exists, create a new Person object
                        if (
                            addressee_first_name == "None"
                            and addressee_last_name == "None"
                            and addressee_entity_name
                        ):
                            addressee = Person.objects.create(
                                entity_name=addressee_entity_name,
                                entity_type=addressee_entity_type,
                            )
                        # If either first_name or last_name exists, try to get the Person object
                        elif (
                            addressee_first_name != "None"
                            or addressee_last_name != "None"
                        ):
                            addressee = Person.objects.filter(
                                first_name=addressee_first_name,
                                last_name=addressee_last_name,
                            ).first()

                        # If there is no Person object and entity_name exists, create a new Person object
                        if not addressee and addressee_entity_name:
                            addressee = Person.objects.create(
                                first_name=addressee_first_name
                                if addressee_first_name != "None"
                                else None,
                                last_name=addressee_last_name
                                if addressee_last_name != "None"
                                else None,
                                entity_name=addressee_entity_name,
                                entity_type=addressee_entity_type,
                            )
                        # If there is a Person object, update the entity_name and entity_type
                        elif addressee:
                            addressee.entity_name = addressee_entity_name
                            addressee.entity_type = addressee_entity_type
                            addressee.save()

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"|- Updated addressee entity name for person {addressee_first_name} {addressee_last_name} ({addressee})"
                                    f"\n|-- {addressee_entity_name} - {addressee_entity_type}"
                                )
                            )

                    except Exception as e:
                        logger.exception(
                            "Error processing row %s: %s", index + 2, str(e)
                        )
                        raise e

        except Exception as e:
            logger.exception("Error reading Excel file: %s", str(e))
            raise e
