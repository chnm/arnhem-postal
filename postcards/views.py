from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpRequest
from .models import Postcard
from .forms import PostcardForm

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

def get_postcard(request: HttpRequest):
    postcard = Postcard.objects.all()
    return postcard

def postcard_details(request: HttpRequest, postcard_id: int):
    postcard = get_object_or_404(Postcard, pk=postcard_id)
    nav_links = get_nav_links("")
    ctx = {
        "postcard": postcard,
        "nav_links": nav_links,
    }
    return render(request, "postcards/book_details.html", ctx)

def library(request: HttpRequest):
    nav_links = get_nav_links("postcard")
    books = get_postcard(request)
    ctx = {
        "nav_links": nav_links,
        "books": books,
    }
    return render(request, "postcards/postcards.html", ctx)

def add_postcard(request: HttpRequest):
    form = PostcardForm(request.POST or None)
    nav_links = get_nav_links("")
    ctx = {
        "form": form,
        "nav_links": nav_links,
    }
    return render(request, "postcards/edit_book.html", ctx)


def add_book(request: HttpRequest):
    form = PostcardForm(request.POST or None)
    nav_links = get_nav_links("")
    ctx = {
        "form": form,
        "nav_links": nav_links,
    }
    if request.method == "POST":
        if form.is_valid():
            form.save()
            postcard = form.instance
            return redirect(reverse("book", kwargs={"postcard_id":postcard.pk}))

    return render(request, "reading_journal/edit_book.html", ctx)