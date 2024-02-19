from django import forms
from django.db.models import Q

from postcards.models import Object, Person


class MapObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = ["date_of_correspondence"]
