from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("exhibits/", views.exhibits, name="exhibits"),
    path("map/", views.mapinterface, name="map"),
    path("timeline/", views.timeline, name="timeline"),
    path("items/", views.ItemHtmxTableView.as_view(), name="table"),
    path("items/<int:id>/", views.object_details, name="postal-item"),
    # path('login/', auth_views.LoginView.as_view(template_name='postal/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='postal/logout.html'), name='logout'),
    # path('profile/', users_views.profile, name='profile'),
    path("taggit/", include("taggit_selectize.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
