from django.conf import settings
from django.conf.urls.static import static
from django.db.models import Prefetch, Q
from django.urls import include, path

from . import views
from .serializers import router

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("exhibits/", views.exhibits, name="exhibits"),
    path(
        "exhibits/evolution/",
        views.evolution_of_holocaust,
        name="evolution_of_holocaust",
    ),
    path(
        "exhibits/evolution-2/",
        views.evolution_of_holocaust_2,
        name="evolution_of_holocaust_2",
    ),
    path(
        "exhibits/evolution-3/",
        views.evolution_of_holocaust_3,
        name="evolution_of_holocaust_3",
    ),
    path(
        "exhibits/evolution-4/",
        views.evolution_of_holocaust_4,
        name="evolution_of_holocaust_4",
    ),
    path(
        "exhibits/evolution-5/",
        views.evolution_of_holocaust_5,
        name="evolution_of_holocaust_5",
    ),
    path(
        "exhibits/evolution-6/",
        views.evolution_of_holocaust_6,
        name="evolution_of_holocaust_6",
    ),
    path(
        "exhibits/evolution-7/",
        views.evolution_of_holocaust_7,
        name="evolution_of_holocaust_7",
    ),
    path(
        "exhibits/evolution-8/",
        views.evolution_of_holocaust_8,
        name="evolution_of_holocaust_8",
    ),
    path(
        "exhibits/evolution-9/",
        views.evolution_of_holocaust_9,
        name="evolution_of_holocaust_9",
    ),
    path(
        "exhibits/boa/",
        views.battle_of_arnhem,
        name="battle_of_arnhem",
    ),
    path(
        "exhibits/boa-2/",
        views.battle_of_arnhem_2,
        name="battle_of_arnhem_2",
    ),
    path(
        "exhibits/boa-3/",
        views.battle_of_arnhem_3,
        name="battle_of_arnhem_3",
    ),
    path("map/", views.mapinterface, name="map"),
    path("timeline/", views.timeline, name="timeline"),
    path("resources/", views.resources, name="resources"),
    path("items/", views.ItemHtmxTableView.as_view(), name="table"),
    path("items/<int:id>/", views.object_details, name="items"),
    path("person/<int:id>/", views.person_details, name="person"),
    # path('login/', auth_views.LoginView.as_view(template_name='postal/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='postal/logout.html'), name='logout'),
    # path('profile/', users_views.profile, name='profile'),
    path("taggit/", include("taggit_selectize.urls")),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
