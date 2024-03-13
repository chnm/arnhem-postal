from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from maps.forms import MapObjectForm
from postcards.filters import ObjectFilter
from postcards.models import Image, Object, Person
from postcards.serializers import PostalObjectSerializer


class PostalObjectsViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = PostalObjectSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ObjectFilter


def maps(request):
    mapbox_access_token = "pk.eyJ1IjoiaGVwcGxlcmoiLCJhIjoiY2xwc3cyN3UyMDdlOTJqbTgwcmZjeWJuYSJ9.wmrR3E8vqsQb3Ml7v0HX-A"

    form = MapObjectForm(request.GET or None)
    if form.is_valid():
        name = form.cleaned_data.get("person")
        data = Object.objects.filter(
            Q(sender_name__full_name=name) | Q(addressee_name__full_name=name)
        )
    else:
        data = Object.objects.all()

    return render(
        request,
        "maps/index.html",
        {
            "mapbox_access_token": mapbox_access_token,
            "form": form,
            "data": data,
        },
    )


def get_images(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    images = Image.objects.filter(person=person)
    return JsonResponse({"images": images})
