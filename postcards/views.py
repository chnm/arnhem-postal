from django.core.paginator import EmptyPage, Paginator
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from postcards.filters import ObjectFilter
from postcards.models import Location, Object, Person, Postmark
from postcards.tables import ItemHtmxTable


def filtered_person_data(request):
    filtered_data = Person.objects.all()
    data = list(
        filtered_data.vlaues("first_name", "last_name", "latitude", "longitude")
    )
    return JsonResponse(data, safe=False)


def get_nav_links(current_page: str):
    """Navigation links for the site."""
    nav_links = {
        "about": {
            "active": False,
            "text": "About",
            "href": "about/",
        },
        "exhibits": {
            "active": False,
            "text": "Exhibits",
            "href": "exhibits/",
        },
        "map": {
            "active": False,
            "text": "Map",
            "href": "map/",
        },
        "timeline": {
            "active": False,
            "text": "Timeline",
            "href": "timeline/",
        },
        "items": {
            "active": False,
            "text": "Browse Items",
            "href": "items/",
        },
    }
    if current_page in nav_links:
        nav_links[current_page]["active"] = True
    return list(nav_links.values())


def index(request: HttpRequest):
    nav_links = get_nav_links("index")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/index.html", ctx)


def about(request: HttpRequest):
    nav_links = get_nav_links("index")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/about.html", ctx)


def exhibits(request: HttpRequest):
    nav_links = get_nav_links("exhibits")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/exhibits.html", ctx)


def evolution_of_holocaust(request: HttpRequest):
    nav_links = get_nav_links("exhibits")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/evolution_of_holocaust.html", ctx)

def evolution_of_holocaust_2(request: HttpRequest):
    nav_links = get_nav_links("exhibits")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/evolution_of_holocaust_2.html", ctx)


def timeline(request: HttpRequest):
    nav_links = get_nav_links("timeline")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/timeline.html", ctx)


def resources(request: HttpRequest):
    nav_links = get_nav_links("resources")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/resources.html", ctx)


def mapinterface(request: HttpRequest):
    person = get_object_or_404(Person, pk=id)
    postal_material = (
        person.sender_objects.all()
        .union(person.addressee_objects.all())
        .order_by("date_of_correspondence")
    )
    nav_links = get_nav_links("map")
    ctx = {
        "nav_links": nav_links,
        "postal_material": postal_material,
    }
    return render(request, "postal/map.html", ctx)


def table(request: HttpRequest):
    nav_links = get_nav_links("items")
    ctx = {
        "nav_links": nav_links,
        "is_database_page": True,
    }
    return render(request, "postal/item_table.html", ctx)


def get_object(request: HttpRequest):
    postal_object = Object.objects.all()
    return postal_object


def object_details(request: HttpRequest, id: int):
    postal_object = get_object_or_404(Object, pk=id)
    nav_links = get_nav_links("")
    ctx = {
        "object": postal_object,
        "nav_links": nav_links,
    }
    return render(request, "postal/object_details.html", ctx)


def person_details(request: HttpRequest, id: int):
    person = get_object_or_404(Person, pk=id)
    postal_material = (
        person.sender_objects.all()
        .union(person.addressee_objects.all())
        .order_by("date_of_correspondence")
    )
    nav_links = get_nav_links("")
    ctx = {
        "person": person,
        "sender_objects": postal_material,
        "nav_links": nav_links,
    }
    return render(request, "postal/person_details.html", ctx)


class CustomPaginator(Paginator):
    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except EmptyPage:
            if int(number) > 1:
                # return the last page
                return self.num_pages
            elif int(number) < 1:
                # return the first page
                return 1
            else:
                raise


# this will render the table
class ItemHtmxTableView(SingleTableMixin, FilterView):
    table_class = ItemHtmxTable
    queryset = Object.objects.all()
    filterset_class = ObjectFilter
    paginate_by = 10
    paginator_class = CustomPaginator

    def get_postmarks(self):
        postmarks = [str(postmark) for postmark in Postmark.objects.all()]
        return postmarks

    def get_location_data(self, field_name):
        location_data = list(
            Location.objects.exclude(**{field_name: None})
            .values_list(field_name, flat=True)
            .distinct()
        )
        return sorted(location_data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_database_page"] = True
        context["postmarks"] = self.get_postmarks()
        context["cities_list"] = self.get_location_data("town_city")
        context["states_list"] = self.get_location_data("province_state")
        return context

    # adjust the template depending on whether an htmx request was made
    def get_template_names(self):
        if self.request.htmx:
            template_name = "postal/item_table_partial.html"
        else:
            template_name = "postal/item_base_table.html"

        return template_name
