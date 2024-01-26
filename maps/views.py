from django.shortcuts import render

from postcards.models import Censor, Object, Person


def maps(request):
    postal_objects = Object.objects.all()
    persons = Person.objects.all()
    censored_postal_objects = Censor.objects.all()
    mapbox_access_token = "pk.eyJ1IjoiaGVwcGxlcmoiLCJhIjoiY2xwc3cyN3UyMDdlOTJqbTgwcmZjeWJuYSJ9.wmrR3E8vqsQb3Ml7v0HX-A"
    return render(
        request,
        "maps/index.html",
        {
            "mapbox_access_token": mapbox_access_token,
            "postal_objects": postal_objects,
            "persons": persons,
            "censored_postal_objects": censored_postal_objects,
        },
    )
