import logging
import os
import re

from dateutil.parser import parse
from django.core.files import File
from django.core.management.base import BaseCommand

from postcards.models import Image, Object

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Associate manually-added images from the static/images/ directory to the data objects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--filepath",
            type=str,
            help="The path to the local images",
            default="static/upload",
        )

    def handle(self, *args, **options):
        filepath = options["filepath"]
        for filename in os.listdir(filepath):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                parts = re.split(
                    "_|-", os.path.splitext(filename)[0]
                )  # Split the string on either an underscore or a dash
                item_id = "_".join(
                    parts[:-1]
                ).strip()  # Join the parts of the item_id back into a string
                caption = parts[-1].strip()  # The last part is the caption
                try:
                    obj = Object.objects.get(item_id=item_id)
                    with open(os.path.join(filepath, filename), "rb") as f:
                        if caption == "Front":
                            img = Image(
                                postcard=obj, image_caption="Front"
                            )  # Set the image_caption field to 'Front'
                        elif caption == "Reverse":
                            img = Image(
                                postcard=obj, image_caption="Reverse"
                            )  # Set the image_caption field to 'Reverse'
                        else:
                            img = Image(
                                postcard=obj
                            )  # If neither 'Front' nor 'Reverse' is in the filename, don't set the image_caption field
                        img.image.save(
                            filename, File(f)
                        )  # Save the image file to the Image instance
                        img.save()  # Save the Image instance
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully updated image for Object "
                            )
                            + self.style.WARNING(f"{item_id}")
                            + self.style.SUCCESS(f" for image ")
                            + self.style.WARNING(f"{filename}")
                        )
                except Object.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Object {item_id} does not exist for image {filename}"
                        )
                    )
