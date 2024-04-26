"""The following removes duplicate Objects by their item_id field.
This has not been strongly tested, so please be careful when running this command.
"""


from django.core.management.base import BaseCommand
from django.db.models import Count

from postcards.models import Object


class Command(BaseCommand):
    help = "Remove duplicate Objects by their item_id field."

    def handle(self, *args, **options):
        duplicates = (
            Object.objects.values("item_id")
            .annotate(item_count=Count("item_id"))
            .filter(item_count__gt=1)
        )
        for duplicate in duplicates:
            item_id = duplicate["item_id"]
            Object.objects.filter(item_id=item_id).delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully removed duplicate Objects with item_id: {item_id}"
                )
            )
        self.stdout.write(
            self.style.SUCCESS("Successfully removed all duplicate Objects")
        )
