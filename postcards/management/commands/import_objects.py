#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction

from postcards.models import Archive, Collection, Object, Person


class Command(BaseCommand):
    help = "Import postal item data from the CSV files"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = Object

    def insert_objects_to_db(self, data):
        try:
            # We create the object and assign appropriate cvs columns to the model fields.
            # For this to work, we need to avoid the instance error. To do that,
            # we need to create the instance first, then save it.
            # We also need to create the related objects first, then save them.
            # We also need to check if the related objects already exist in the db.

            # Create the related objects
            # Create the archive
            archive, created = Archive.objects.get_or_create(
                location=Archive.objects.filter(location="Box 1 Folders I-VIII").first()
            )
            # Create the collection
            collection, created = Collection.objects.get_or_create(
                name=Collection.objects.filter(name="Tim Gale").first()
            )

            # Create the sender
            sender, created = Person.objects.get_or_create(
                first_name=data["sender_first_name"],
                last_name=data["sender_last_name"],
            )

            # Create the addressee
            addressee, created = Person.objects.get_or_create(
                first_name=data["addressee_first_name"],
                last_name=data["addressee_last_name"],
            )

            # Now use set() to create the many-to-many relationship
            Object.objects.set("sender_name", sender)
            Object.objects.set("addressee_name", addressee)
            Object.objects.set("collection", collection)
            Object.objects.set("collection_location", archive)
            Object.objects.set("date_of_correspondence", data["date_of_correspondence"])
            Object.objects.set("letter_type", data["type_(postcard/letter/package)"])
            Object.objects.set("letter_enclosed", data["letter_enclosed_(yes/no)"])
            Object.objects.set("return_to_sender", data["return_to_sender"])
            Object.objects.set("date_returned", data["date_returned_to_sender"])
            Object.objects.set("regime_censor", data["censor"])
            Object.objects.set("public_notes", data["notes"])

            # Create the object
            # object_instance = Object(
            #     collection=collection,
            #     collection_location=archive,
            #     sender_name=sender,
            #     addressee_name=addressee,
            #     date_of_correspondence=data['date_of_correspondence'],
            #     letter_type=data['type_(postcard/letter/package)'],
            #     letter_enclosed=data['letter_enclosed_(yes/no)'],
            #     return_to_sender=data['return_to_sender'],
            #     date_returned=data['date_returned_to_sender'],
            #     regime_censor=data['censor'],
            #     public_notes=data['notes'],
            # )

            # # Save the object
            # object_instance.save()

            # self.model_name.objects.create(
            #     collection=collection,
            #     collection_location=collection_location,
            #     sender_name=sender,
            #     addressee_name=addressee,
            #     date_of_correspondence=data['date_of_correspondence'],
            #     letter_type=data['type_(postcard/letter/package)'],
            #     letter_enclosed=data['letter_enclosed_(yes/no)'],
            #     return_to_sender=data['return_to_sender'],
            #     date_returned=data['date_returned_to_sender'],
            #     regime_censor=data['censor'],
            #     public_notes=data['notes'],
            # )
        except Exception as e:
            raise CommandError(
                "Encountered an error inserting {}: {}".format(self.model_name, e)
            )

    def add_arguments(self, parser):
        parser.add_argument("filename", nargs="+", type=str, help="CSV file to import")

    def handle(self, *args, **kwargs):
        filename = kwargs["filename"][0]
        self.stdout.write(
            self.style.SUCCESS("Importing {} from {}".format(self.model_name, filename))
        )
        with open(filename, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            # check that reader worked
            if reader is None:
                raise CommandError(self.style.ERROR("Error reading CSV file"))
            else:
                self.stdout.write(self.style.SUCCESS("Successfully read CSV file"))
            with transaction.atomic():
                for row in reader:
                    self.insert_objects_to_db(row)
        reader.close()
