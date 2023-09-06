from django import forms

from .models import Object, Postmark


class ObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = ["tags"]


class PostmarkForm(forms.ModelForm):
    class Meta:
        model = Postmark
        fields = ["location"]
