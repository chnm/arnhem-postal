import logging
import math
from datetime import datetime

import numpy as np
import pandas as pd
from dateutil.parser import parse
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from postcards.models import Location

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load location data from an Excel file for the postal objects."

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
            logger.exception(f"Error loading data: {str(e)}")
            self.stdout.write(
                self.style.ERROR("Error loading data. Check logs for details.")
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

                        addressee_town_city = str(row["addressee town/city"]).strip()
                        addressee_province_state = str(
                            row["addressee province/state"]
                        ).strip()
                        addressee_country = str(row["addressee country"]).strip()
                        sender_town_city = str(row["sender town/city"]).strip()
                        sender_province_state = str(
                            row["sender province/state"]
                        ).strip()
                        sender_country = str(row["sender country"]).strip()

                        postmark_1_location_name = str(
                            row["postmark 1 location"]
                        ).strip()
                        postmark_2_location_name = str(
                            row["postmark 2 location"]
                        ).strip()

                        try:
                            (
                                addressee_location,
                                created,
                            ) = Location.objects.get_or_create(
                                town_city=addressee_town_city,
                                province_state=addressee_province_state,
                                country=addressee_country,
                            )
                        except MultipleObjectsReturned:
                            addressee_location = Location.objects.filter(
                                town_city=addressee_town_city,
                                province_state=addressee_province_state,
                                country=addressee_country,
                            ).first()

                        try:
                            sender_location, created = Location.objects.get_or_create(
                                town_city=sender_town_city,
                                province_state=sender_province_state,
                                country=sender_country,
                            )
                        except MultipleObjectsReturned:
                            sender_location = Location.objects.filter(
                                town_city=sender_town_city,
                                province_state=sender_province_state,
                                country=sender_country,
                            ).first()

                        try:
                            (
                                postmark_1_location,
                                created,
                            ) = Location.objects.get_or_create(
                                town_city=postmark_1_location_name
                            )
                        except MultipleObjectsReturned:
                            postmark_1_location = Location.objects.filter(
                                town_city=postmark_1_location_name
                            ).first()

                        try:
                            (
                                postmark_2_location,
                                created,
                            ) = Location.objects.get_or_create(
                                town_city=postmark_2_location_name
                            )
                        except MultipleObjectsReturned:
                            postmark_2_location = Location.objects.filter(
                                town_city=postmark_2_location_name
                            ).first()
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Error processing row {index + 2} of sheet {sheet_name}: {str(e)}"
                            )
                        )
                        raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {str(e)}"))
            raise
        finally:
            xls.close()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Finished loading data from file {file_path} and sheet {sheet_name}"
                )
            )
