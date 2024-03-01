from django.conf import settings
from django.conf.urls.static import static
from django.db.models import Prefetch, Q
from django.urls import include, path
from rest_framework import routers, serializers, viewsets

from postcards.models import Censor, Image, Object, Person, Postmark

from . import views


class PersonsSerializer(serializers.HyperlinkedModelSerializer):
    # postal_objects = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(view_name="person-detail")
    # associated_routes = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = [
            "person_id",
            "url",
            "first_name",
            "last_name",
            "latitude",
            "longitude",
        ]

    # def get_postal_objects(self, obj):
    #     postal_objects = Object.objects.filter(
    #         Q(sender_name=obj) | Q(addressee_name=obj)
    #     ).prefetch_related(
    #         Prefetch("images", queryset=Image.objects.all(), to_attr="related_images")
    #     )

    #     return [
    #         {
    #             "sender_name__first_name": postal_object.sender_name.first_name,
    #             "sender_name__last_name": postal_object.sender_name.last_name,
    #             "addressee_name__first_name": postal_object.addressee_name.first_name,
    #             "addressee_name__last_name": postal_object.addressee_name.last_name,
    #             "date_of_correspondence": postal_object.date_of_correspondence,
    #             "return_to_sender": postal_object.return_to_sender,
    #             "date_returned": postal_object.date_returned,
    #             "reasonreturn": postal_object.reason_for_return_original,
    #             "letter_enclosed": postal_object.letter_enclosed,
    #             "regime_censor": postal_object.regime_censor,
    #             "public_notes": postal_object.public_notes,
    #             "images": [
    #                 {
    #                     "image": image.image.url,
    #                     "image_caption": image.image_caption,
    #                 }
    #                 for image in postal_object.related_images
    #             ],
    #         }
    #         for postal_object in postal_objects
    #     ]

    # def get_associated_routes(self, obj):
    #     """We want to get the routes associated with a person. We use the person_id to get the routes
    #     associated with the person. We then return the routes as a list of dictionaries."""
    #     routes = []
    #     postal_objects = Object.objects.filter(
    #         Q(sender_name=obj) | Q(addressee_name=obj)
    #     )
    #     for postal_object in postal_objects:
    #         route = postal_object.calculate_route()
    #         routes.append(route)
    #     return routes


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonsSerializer


class LocationSerializer(serializers.Serializer):
    def get_location(self, obj):
        return {
            "latitude": obj.latitude,
            "longitude": obj.longitude,
        }


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["image", "image_caption"]


class PostmarksSerializer(serializers.HyperlinkedModelSerializer):
    latitude = serializers.ReadOnlyField(source="location.latitude")
    longitude = serializers.ReadOnlyField(source="location.longitude")

    class Meta:
        model = Postmark
        fields = (
            "date",
            "latitude",
            "longitude",
        )


class PostmarkViewSet(viewsets.ModelViewSet):
    queryset = Postmark.objects.all()
    serializer_class = PostmarksSerializer


class CensorSerializer(LocationSerializer, serializers.HyperlinkedModelSerializer):
    latitude = serializers.ReadOnlyField(source="censor_location.latitude")
    longitude = serializers.ReadOnlyField(source="censor_location.longitude")

    class Meta:
        model = Censor
        fields = (
            "censor_name",
            "latitude",
            "longitude",
        )

    def get_censor_location(self, obj):
        return self.get_location(obj)


class CensorViewSet(viewsets.ModelViewSet):
    queryset = Censor.objects.all()
    serializer_class = CensorSerializer


class PostalObjectSerializer(serializers.HyperlinkedModelSerializer):
    sender_name = PersonsSerializer()
    addressee_name = PersonsSerializer()
    postmark = PostmarksSerializer(many=True)
    latitude = serializers.ReadOnlyField(source="sender_name.location.latitude")
    longitude = serializers.ReadOnlyField(source="sender_name.location.longitude")
    route = serializers.SerializerMethodField()

    class Meta:
        model = Object
        fields = (
            "sender_name",
            "addressee_name",
            "postmark",
            "latitude",
            "longitude",
            "route",
        )

    def get_regime_location(self, obj):
        return self.get_location(obj)

    def get_route(self, obj):
        return obj.calculate_route()


class PostalObjectViewSet(viewsets.ModelViewSet):
    queryset = Object.objects.all()
    serializer_class = PostalObjectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            "sender_name", "addressee_name"
        ).prefetch_related("images")
        return queryset


router = routers.DefaultRouter()
router.register(r"people", PersonViewSet)
router.register(r"postmarks", PostmarkViewSet)
router.register(r"censors", CensorViewSet)
router.register(r"objects", PostalObjectViewSet)


urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("exhibits/", views.exhibits, name="exhibits"),
    path("map/", views.mapinterface, name="map"),
    path("timeline/", views.timeline, name="timeline"),
    path("items/", views.ItemHtmxTableView.as_view(), name="table"),
    path("items/<int:id>/", views.object_details, name="items"),
    # path('login/', auth_views.LoginView.as_view(template_name='postal/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(template_name='postal/logout.html'), name='logout'),
    # path('profile/', users_views.profile, name='profile'),
    path("taggit/", include("taggit_selectize.urls")),
    path("api/", include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
