from django.core.paginator import EmptyPage, Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from postcards.filters import ItemFilter
from postcards.forms import ObjectForm
from postcards.models import Object
from postcards.tables import ItemHTMxMultiColumnTable


def get_nav_links(current_page: str):
    nav_links = {
        "index": {"active": False, "text": "Home", "href": reverse("index")},
        "collections": {
            "active": False,
            "text": "Collections",
            "href": "#",
        },
        "library": {
            "active": False,
            "text": "Library",
            "href": "#",
        },
        "admin": {
            "active": False,
            "text": "Admin",
            "href": reverse("admin:index"),
        },
    }
    if current_page in nav_links:
        nav_links[current_page]["active"] = True
    return list(nav_links.values())


def index(request: HttpRequest):
    nav_links = get_nav_links("index")
    ctx = {"nav_links": nav_links}
    return render(request, "postcards/index.html", ctx)


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
    return render(request, "postcards/book_details.html", ctx)


def library(request: HttpRequest):
    nav_links = get_nav_links("postcard")
    objects = get_object(request)
    ctx = {
        "nav_links": nav_links,
        "books": objects,
    }
    return render(request, "postcards/postcards.html", ctx)


def add_object(request: HttpRequest):
    form = ObjectForm(request.POST or None)
    nav_links = get_nav_links("")
    ctx = {
        "form": form,
        "nav_links": nav_links,
    }
    return render(request, "postcards/edit_object.html", ctx)


def add_object(request: HttpRequest):
    form = ObjectForm(request.POST or None)
    nav_links = get_nav_links("")
    ctx = {
        "form": form,
        "nav_links": nav_links,
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            object = form.instance
            return redirect(reverse("object", kwargs={"id": object.pk}))

    return render(request, "postcards/edit_object.html", ctx)


class CustomPaginator(Paginator):
    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except EmptyPage:
            if int(number) > 1:
                return self.num_pages
            elif int(number) < 1:
                return 1
            else:
                raise


class ItemHTMxMultiColumnTableView(SingleTableMixin, FilterView):
    table_class = ItemHTMxMultiColumnTable
    queryset = Object.objects.all()
    filterset_class = ItemFilter
    paginate_by = 25
    paginator_class = CustomPaginator

    def get_template_names(self):
        if self.request.htmx:
            template_name = "postcards/item_table_partial.html"
        else:
            template_name = "postcards/item_table_col_filter.html"

        return template_name


def item_table(request: HttpRequest):
    table = ItemHTMxMultiColumnTable(Object.objects.all())
    ctx = {"table": table}
    return render(request, "tables/item_col_filter.html", ctx)
