import django_filters
from django.db.models import Q
from django.shortcuts import render

from postcards.models import Collection, Location, Object, Person, Postmark


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


class ObjectFilter(django_filters.FilterSet):
    class Meta:
        model = Object
        fields = [
            "correspondence",
            "date",
            "collection",
        ]

    correspondence = django_filters.ChoiceFilter(
        choices=combine_all_names(),
        method="filter_query",
        label="Writer",
        empty_label="Select a writer",
    )
    date = django_filters.CharFilter(
        field_name="date_of_correspondence",
        lookup_expr="icontains",
    )
    collection = django_filters.ModelChoiceFilter(
        field_name="collection",
        queryset=Collection.objects.all(),
        to_field_name="name",
    )

    def filter_query(self, queryset, name, value):
        """Filter the queryset by the sender or addressee name."""
        first_name, last_name = value.split(" ")
        return queryset.filter(
            Q(sender_name__first_name=first_name, sender_name__last_name=last_name)
            | Q(
                addressee_name__first_name=first_name,
                addressee_name__last_name=last_name,
            )
        )
