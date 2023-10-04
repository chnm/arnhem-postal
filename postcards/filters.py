import django_filters
from django.db.models import Q
from django_filters import FilterSet

from postcards.models import Object


class ItemFilter(FilterSet):
    query = django_filters.CharFilter(method="universal_search", label="")

    class Meta:
        model = Object
        fields = ["addressee_name", "sender_name"]

    def universal_search(self, queryset, name, value):
        return queryset.filter(
            Q(addressee_name__icontains=value) | Q(sender_name__icontains=value)
        )
