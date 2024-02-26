from django.core.paginator import EmptyPage, Paginator
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, render
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from rest_framework import generics

from postcards.filters import ObjectFilter
from postcards.models import Object, Person
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


def timeline(request: HttpRequest):
    nav_links = get_nav_links("timeline")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/timeline.html", ctx)


def mapinterface(request: HttpRequest):
    nav_links = get_nav_links("map")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/map.html", ctx)


def table(request: HttpRequest):
    nav_links = get_nav_links("items")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/item_table.html", ctx)


def get_object(request: HttpRequest):
    object = Object.objects.all()
    return object


def object_details(request: HttpRequest, id: int):
    object = get_object_or_404(Object, pk=id)
    nav_links = get_nav_links("")
    ctx = {
        "object": object,
        "nav_links": nav_links,
    }
    return render(request, "postal/object_details.html", ctx)


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

    # adjust the template depending on whether an htmx request was made
    def get_template_names(self):
        if self.request.htmx:
            template_name = "postal/item_table_partial.html"
        else:
            template_name = "postal/item_base_table.html"

        return template_name
