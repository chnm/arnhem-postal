import pandas as pd
from django.core.management.base import BaseCommand

from postcards.models import Location, Person


class Command(BaseCommand):
    help = "Load data from an Excel file into Person and Location models"

    def handle(self, *args, **options):
        file_path = "~/Dropbox/30-39 Projects/30.06 CHNM/Projects/Arnhem/arnhem.xlsx"
        self.load_data(file_path)
        self.stdout.write(self.style.SUCCESS("Data loaded successfully"))

    def load_data(self, file_path):
        df = pd.read_excel(file_path, sheet_name="Box 1 Folders I-VIII")

        for index, row in df.iterrows():
            # Extract data from the row
            addressee_first_name = str(row["Addressee First Name"])
            addressee_last_name = str(row["Addressee Last Name"])
            addressee_title = str(row["Addressee Title"])
            addressee_town = str(row["Addressee Town/City"])
            addressee_state = str(row["Addressee Province/State"])
            addressee_country = str(row["Addressee Country"])

            sender_first_name = str(row["Sender First Name"])
            sender_last_name = str(row["Sender Last Name"])
            sender_title = str(row["Sender Title"])
            sender_town = str(row["Sender Town/City"])
            sender_state = str(row["Sender Province/State"])
            sender_country = str(row["Sender Country"])

            # Create or update Addressee Location
            addressee_location, _ = Location.objects.get_or_create(
                town_city=addressee_town,
                province_state=addressee_state,
                country=addressee_country,
            )

            # Create or update Addressee Person
            addressee, _ = Person.objects.get_or_create(
                first_name=addressee_first_name,
                last_name=addressee_last_name,
                title=addressee_title,
                location=addressee_location,
            )

            # Create or update Sender Location
            sender_location, _ = Location.objects.get_or_create(
                town_city=sender_town,
                province_state=sender_state,
                country=sender_country,
            )

            # Create or update Sender Person
            sender, _ = Person.objects.get_or_create(
                first_name=sender_first_name,
                last_name=sender_last_name,
                title=sender_title,
                location=sender_location,
            )
