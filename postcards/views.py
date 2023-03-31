from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpRequest
from .models import Object
from .forms import ObjectForm

def get_nav_links(current_page: str):
    nav_links = {
        "index":
            {
                "active": False,
                "text": "Home",
                "href": reverse("index")
            },
        "collections":
            {
                "active": False,
                "text": "Collections",
                "href": "#",
            },
        "library":
            {
                "active": False,
                "text": "Library",
                "href": "#",
            },
        "admin":
            {
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
            return redirect(reverse("object", kwargs={"id":object.pk}))

    return render(request, "postcards/edit_object.html", ctx)