from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("postcard/", views.get_object, name="object"),
    path("postcard/<int:id>/", views.object_details, name="object"),
    path("taggit/", include("taggit_selectize.urls")),
    path("table/", views.ItemTableView.as_view(), name="table"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
