import logging
import math
from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.parser import parse
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from postcards.models import Object, Person

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

                        item_number = str(row["item number"])
                        sender_entity_name = str(row["entitiy"])
                        sender_entity_type = str(
                            row["sender correspondence type"]
                        ).lower()
                        addressee_entity_name = str(row["addressee entity"])
                        addressee_entity_type = str(
                            row["addresse correspondence type"]
                        ).lower()

                        # Get the Object with the given item_number
                        objs = Object.objects.filter(item_id=item_number)

                        for obj in objs:
                            obj.sender_name.entity_name = sender_entity_name
                            obj.sender_name.entity_type = sender_entity_type
                            obj.sender_name.save()

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"|- Updated sender entity name for object {item_number} ({obj.sender_name})"
                                    f"\n|-- {sender_entity_name} - {sender_entity_type}"
                                )
                            )

                            obj.addressee_name.entity_name = addressee_entity_name
                            obj.addressee_name.entity_type = addressee_entity_type
                            obj.addressee_name.save()

                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"|- Updated addressee entity name for object {item_number} ({obj.addressee_name})"
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
