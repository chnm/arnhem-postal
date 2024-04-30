import os
import re

from dateutil.parser import parse
from django.core.files import File
from django.core.management.base import BaseCommand

from postcards.models import Image, PrimarySource


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--filepath",
            type=str,
            help="The path to the local images",
            default="static/upload",
        )

    def handle(self, *args, **options):
        filepath = options["filepath"]

        for prefix in ["XVIII", "XLIV"]:
            self.stdout.write(
                self.style.SUCCESS(f"Processing item ")
                + self.style.WARNING(f"{prefix}")
            )
            files = os.listdir(filepath)

            item_files = [f for f in files if re.match(f"^{prefix}\d+", f)]
            for item_file in item_files:
                try:
                    item_id = re.match(f"^{prefix}\d+", item_file).group(0)
                    primary_source = PrimarySource.objects.get(item_id=item_id)

                    with open(os.path.join(filepath, item_file), "rb") as f:
                        image = Image.objects.create(
                            primary_source=primary_source,
                            image=File(f),
                            image_caption=item_file,
                        )
                        image.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully updated image for PrimarySource "
                            )
                            + self.style.WARNING(f"{item_id}")
                            + self.style.SUCCESS(" for image ")
                            + self.style.WARNING(f"{item_file}")
                        )
                except PrimarySource.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"No PrimarySource found with item_id {item_id}"
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"An error occurred while processing item_id {item_id} and file {item_file}: {str(e)}"
                        )
                    )
