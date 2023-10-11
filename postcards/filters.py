import django_filters
from django.db.models import Q

from postcards.models import Collection, Object


def combine_all_names():
    """Combine all possible names from the Object senders and
    addressees for the dropdown."""
    # get all the names from the Object senders and addressees
    if Object.objects.all().values("sender_name") == "NA NA":
        pass
    sender_names = (
        Object.objects.all()
        .order_by("sender_name")
        .values_list("sender_name", "sender_name")
    )
    if Object.objects.all().values("addressee_name") == "NA NA":
        pass
    addressee_names = (
        Object.objects.all()
        .order_by("addressee_name")
        .values_list("addressee_name", "addressee_name")
    )
    # combine the names
    all_names = list(sender_names) + list(addressee_names)

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
        return queryset.filter(
            Q(sender_name=value) | Q(addressee_name=value)
        ).distinct()
