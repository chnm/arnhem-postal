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

    correspondence_date = Object.objects.values_list(
        "date_of_correspondence", flat=True
    )
    selected_person = request.GET.get("person")
    people = Person.objects.all()

    if selected_person:
        people = people.filter(
            Q(sender_name__first_name=selected_person)
            | Q(addressee_name__first_name=selected_person)
            | Q(sender_name__last_name=selected_person)
            | Q(addressee_name__last_name=selected_person)
        )

    people_data = [
        {
            "id": person.person_id,
            "first_name": person.first_name,
            "last_name": person.last_name,
        }
        for person in people
    ]

    form = MapObjectForm(request.GET or None)
    if form.is_valid():
        name = form.cleaned_data.get("person")
        data = Object.objects.filter(
            Q(sender_name__first_name=name)
            | Q(addressee_name__first_name=name)
            | Q(sender_name__last_name=name)
            | Q(addressee_name__last_name=name)
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
            "people": people_data,
        },
    )


def get_images(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    images = Image.objects.filter(person=person)
    return JsonResponse({"images": images})
