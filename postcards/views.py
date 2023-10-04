from django.core.paginator import EmptyPage, Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from postcards.filters import ItemFilter
from postcards.forms import ObjectForm
from postcards.models import Object
from postcards.tables import ObjectHTMxMultiColumnTable


def get_nav_links(current_page: str):
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
            "href": "table/",
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


def table(request: HttpRequest):
    nav_links = get_nav_links("items")
    ctx = {"nav_links": nav_links}
    return render(request, "postal/htmx.html", ctx)


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


def library(request: HttpRequest):
    nav_links = get_nav_links("items")
    objects = get_object(request)
    ctx = {
        "nav_links": nav_links,
        "objects": objects,
    }
    return render(request, "postal/objects.html", ctx)


class ItemHTMxTableView(SingleTableMixin, FilterView):
    table_class = ObjectHTMxMultiColumnTable
    queryset = Object.objects.all()
    filterset_class = ItemFilter
    paginate_by = 10

    def get_template_names(self):
        if self.request.htmx:
            template_name = ["postal/htmx_partial.html"]
        else:
            template_name = ["postal/htmx.html"]

        return template_name


# class SimpleTable(tables.Table):
#    class Meta:
#       model = Object


# this will render table
class ItemTableView(SingleTableMixin, FilterView):
    table_class = ObjectHTMxMultiColumnTable
    queryset = Object.objects.all()
    filterset_class = ItemFilter
    template_name = "postal/htmx.html"

    class Meta:
        model = Object
