import django_filters
from django.db.models import Q

from postcards.models import Collection, Object


def combine_all_names():
    """Combine all possible names from the Object senders and
    addressees for the dropdown."""

    sender_names = (
        Object.objects.exclude(
            sender_name__first_name="NA", sender_name__last_name="NA"
        )
        .order_by("sender_name__first_name", "sender_name__last_name")
        .values_list("sender_name__first_name", "sender_name__last_name")
    )
    addressee_names = (
        Object.objects.exclude(
            addressee_name__first_name="NA", addressee_name__last_name="NA"
        )
        .order_by("addressee_name__first_name", "addressee_name__last_name")
        .values_list("addressee_name__first_name", "addressee_name__last_name")
    )
    all_names = list(sender_names) + list(addressee_names)
    all_names = [" ".join(map(str, name)) for name in all_names]
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
