from django.urls import path

from .views import AboutPageView
from .views import EvolutionOfHolocaustPageView

urlpatterns = [
    path("about/", AboutPageView.as_view(), name="about"),
    path("evolution-of-holocaust/", EvolutionOfHolocaustPageView.as_view(), name="evolution-of-holocaust"),
]
