import logging
import os

from django.core.files import File
from django.core.management.base import BaseCommand

from postcards.models import Object

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Associate manually-added images from the static/images/ directory to the data objects."

    def add_arguments(self, parser):
        parser.add_arguments(
            "--filepath",
            type=str,
            help="The path to the local images",
            default=os.path.join(os.path.dirname(__file__), "static", "images"),
        )

    def handle(self, *args, **options):
        filepath = options["filepath"]
        for filename in os.listdir(filepath):
            if filename.endswith(".jpg") or filename.endswith(".png"):
                item_id = os.path.splitext(filename)[0]
                try:
                    obj = Object.objects.get(item_id=item_id)
                    with open(os.path.join(filepath, filename), "rb") as f:
                        obj.image.save(filename, File(f))
                        obj.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Successfully updated image for Object {item_id}"
                            )
                        )
                except Object.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"Object {item_id} does not exist")
                    )
