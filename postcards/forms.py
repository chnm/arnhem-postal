from django import forms

from .models import Object, Person, Postmark


class ObjectForm(forms.ModelForm):
    class Meta:
        model = Object
        fields = "__all__"

    sender_name = forms.ModelChoiceField(
        querset=Person.objects.all(),
        label="Sender",
    )

    addressee_name = forms.ModelChoiceField(
        querset=Person.objects.all(),
        label="Addressee",
    )


class PostmarkForm(forms.ModelForm):
    class Meta:
        model = Postmark
        fields = ["location"]
