from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name = "index"),
    path("postcard/", views.get_postcard, name = "postcard"),
    path("postcard/<int:postcard_id>/", views.postcard_details, name = "postcard"),
    path("postcard/add", views.add_postcard, name="add_postcard"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)