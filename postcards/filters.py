import django_filters
from django.db.models import Q
from django.forms import TextInput

from postcards.models import Object


class ItemFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(label="")
    regime_censor = django_filters.CharFilter(label="", lookup_expr="isstartswith")

    class Meta:
        model = Object
        fields = ["id", "regime_censor", "letter_type"]
