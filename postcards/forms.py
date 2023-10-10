from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.html import format_html

from .models import Object, Person, Postmark


class ObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = ["tags"]


class PostmarkForm(forms.ModelForm):
    class Meta:
        model = Postmark
        fields = ["location"]
