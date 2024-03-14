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
        "exhibits/evolution/",
        views.evolution_of_holocaust_pre_war,
        name="evolution_of_holocaust_pre_war",
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
