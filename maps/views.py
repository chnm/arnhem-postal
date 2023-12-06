from django.shortcuts import render

from postcards.models import Object


def maps(request):
    postal_objects = Object.objects.all()
    mapbox_access_token = "pk.eyJ1IjoiaGVwcGxlcmoiLCJhIjoiY2xwc3cyN3UyMDdlOTJqbTgwcmZjeWJuYSJ9.wmrR3E8vqsQb3Ml7v0HX-A"
    return render(
        request,
        "maps/index.html",
        {"mapbox_access_token": mapbox_access_token, "postal_objects": postal_objects},
    )
