from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from . import views

urlpatterns = [
    path("maps/", views.maps, name="maps"),
    path("maps/<int:person_id>/", views.get_images, name="get_images"),
]
