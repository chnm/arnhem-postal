# fields.py
from dataclasses import MISSING

from django.db import models
from markdown import markdown

from postcards.utils.sanitizer import clean


class HtmlField(models.TextField):
    """a text field for storing html"""

    def field_from_activity(self, value):
        if not value or value == MISSING:
            return None
        return clean(value)

    def field_to_activity(self, value):
        return markdown(value) if value else value
