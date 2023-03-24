from django import forms
from .models import Postcard

class PostcardForm(forms.ModelForm):
    class Meta:
        model = Postcard
        fields = ['tags']