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


class TownCityFilter(django_filters.ModelChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field.widget.attrs.update(
            {"class": "form-control"}
        )  # Add Bootstrap form-control class
        self.field.queryset = Location.objects.values_list(
            "town_city", flat=True
        ).distinct()


class ProvinceStateFilter(django_filters.ModelChoiceFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field.widget.attrs.update(
            {"class": "form-control"}
        )  # Add Bootstrap form-control class
        self.field.queryset = Location.objects.values_list(
            "province_state", flat=True
        ).distinct()


class ObjectFilter(django_filters.FilterSet):
    class Meta:
        model = Object
        fields = [
            "query",
            "correspondence",
            "date",
            "collection",
            "town_city",
            "province_state",
            "postmark",
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
        label="Date of correspondence",
    )
    collection = django_filters.ModelChoiceFilter(
        field_name="collection",
        queryset=Collection.objects.all(),
        to_field_name="name",
    )
    town_city = TownCityFilter(
        field_name="town_city",
        queryset=Location.objects.all(),
        label="Town/City",
    )
    province_state = ProvinceStateFilter(
        field_name="province_state",
        queryset=Location.objects.all(),
        label="Province/State",
    )
    postmark = django_filters.ModelChoiceFilter(
        field_name="postmark",
        queryset=Postmark.objects.all(),
        to_field_name="location",
    )
    query = django_filters.CharFilter(
        method="filter_query",
        label="Keyword search",
    )

    def filter_query(self, queryset, name, value):
        """Filter the queryset by the sender or addressee name."""
        words = value.split(" ")

        queries = Q()
        for word in words:
            if name == "postmark":
                queries |= Q(postmark__postmark_id__icontains=word)
            elif name == "date":
                queries |= Q(date_of_correspondence__icontains=word)
            else:
                queries |= Q(sender_name__first_name=word)
                queries |= Q(sender_name__last_name=word)
                queries |= Q(addressee_name__first_name=word)
                queries |= Q(addressee_name__last_name=word)
                queries |= Q(location__town_city=word)
                queries |= Q(location__province_state=word)
                queries |= Q(public_notes__icontains=word)

        return queryset.filter(queries)
