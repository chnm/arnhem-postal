import logging

import pandas as pd
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Associate manually-added images from the static/ directory to the data objects."

    def add_arguments(self, parser):
        parser.add_arguments(
            "--filepath", type=str, help="The path to the local images"
        )

    def handle(self, *args, **options):
        print(args)
        print(options)

    def load_data(self):
        print("images")
