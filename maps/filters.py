from functools import reduce

import django_filters
from django.db.models import Q

from postcards.models import Object


def get_names(field_prefix):
    """Get names from the Object model for a given field prefix (sender_name or addressee_name)."""
    return (
        Object.objects.exclude(
            **{f"{field_prefix}__first_name": "NA", f"{field_prefix}__last_name": "NA"}
        )
        .order_by(f"{field_prefix}__first_name", f"{field_prefix}__last_name")
        .values_list(f"{field_prefix}__first_name", f"{field_prefix}__last_name")
    )


def combine_all_names():
    """Combine all possible names from the Object senders and addressees for the dropdown."""
    all_names = list(get_names("sender_name")) + list(get_names("addressee_name"))
    all_names = [" ".join(map(str, name)) for name in all_names]
    all_names = [
        name for i, name in enumerate(all_names) if all_names.index(name) == i
    ]  # Only add names that are not already in the list
    all_names = [(name, name) for name in all_names]

    return all_names
