from django.urls import path

from .views import AboutPageView

urlpatterns = [
    path("about/", AboutPageView.as_view(), name="about"),
    path("evolution-of-holocaust/", AboutPageView.as_view(), name="evolution-of-holocaust"),
]
