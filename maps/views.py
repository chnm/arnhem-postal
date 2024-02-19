from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from maps.forms import MapObjectForm
from postcards.models import Censor, Image, Object, Person


def maps(request):
    postal_objects = Object.objects.all()
    censored_postal_objects = Censor.objects.all()
    mapbox_access_token = "pk.eyJ1IjoiaGVwcGxlcmoiLCJhIjoiY2xwc3cyN3UyMDdlOTJqbTgwcmZjeWJuYSJ9.wmrR3E8vqsQb3Ml7v0HX-A"

    form = MapObjectForm(request.GET or None)
    if form.is_valid():
        name = form.cleaned_data.get("person")
        data = Object.objects.filter(
            Q(sender_name__full_name=name) | Q(addressee_name__full_name=name)
        )
    else:
        data = Object.objects.all()

    persons = Person.objects.all()
    routes = cache.get("routes")

    # If the routes data is not in the cache, calculate it
    if not routes:
        routes = []
        routeid = 0

        for obj in postal_objects:
            if (
                obj.sender_name
                and obj.sender_name.longitude
                and obj.sender_name.latitude
            ):
                start_coords = [
                    float(obj.sender_name.longitude),
                    float(obj.sender_name.latitude),
                ]
                end_coords = None
            else:
                print(
                    f"Skipping postal object {obj.id} due to missing or invalid sender location. Expected longitude and latitude, but got {obj.sender_name.longitude} and {obj.sender_name.latitude} respectively."
                )
                continue

            for postmark in obj.postmark.all():
                if (
                    postmark.location
                    and postmark.location.longitude
                    and postmark.location.latitude
                ):
                    end_coords = [
                        float(postmark.location.longitude),
                        float(postmark.location.latitude),
                    ]
                    routes.append(
                        {
                            "type": "Feature",
                            "properties": {"id": routeid},
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [start_coords, end_coords],
                            },
                        }
                    )
                    start_coords = end_coords
                else:
                    print("Skipping postmark due to missing or invalid location")

            if (
                obj.addressee_name
                and obj.addressee_name.longitude
                and obj.addressee_name.latitude
            ):
                end_coords = [
                    float(obj.addressee_name.longitude),
                    float(obj.addressee_name.latitude),
                ]
                routes.append(
                    {
                        "type": "Feature",
                        "properties": {"id": routeid},
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [start_coords, end_coords],
                        },
                    }
                )
            else:
                print(
                    f"Skipping postal object {obj.id} due to missing or invalid addressee location. Expected longitude and latitude, but got {obj.addressee_name.longitude} and {obj.addressee_name.latitude} respectively."
                )

            routeid += 1

        # Cache the routes data for 5 minutes
        cache.set("routes", routes, 60 * 5)

    return render(
        request,
        "maps/index.html",
        {
            "mapbox_access_token": mapbox_access_token,
            "postal_objects": postal_objects,
            "persons": persons,
            "censored_postal_objects": censored_postal_objects,
            "postal_routes": routes,
            "form": form,
            "data": data,
        },
    )


def get_images(request, person_id):
    person = get_object_or_404(Person, id=person_id)
    images = Image.objects.filter(person=person)
    return JsonResponse({"images": images})
