from django.db.models import Prefetch, Q
from rest_framework import routers, serializers, viewsets

from postcards.models import Censor, Image, Location, Object, Person, Postmark


class AssociatedObjectsSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender_full_name")
    addressee_name = serializers.CharField(source="addressee_full_name")

    class Meta:
        model = Object
        fields = [
            "letter_type",
            "sender_name",
            "addressee_name",
            "date_of_correspondence",
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "location_id",
            "town_city",
            "province_state",
            "country",
            "latitude",
            "longitude",
        ]

    def get_location(self, obj):
        return {
            "latitude": obj.latitude,
            "longitude": obj.longitude,
        }


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


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


class PersonsSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="person-detail")
    location = LocationSerializer(read_only=True)
    # postal_objects = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = [
            "person_id",
            "url",
            "first_name",
            "last_name",
            "house_number",
            "street",
            "location",
            "latitude",
            "longitude",
            # "postal_objects",
        ]

    def get_postal_objects(self, obj):
        addressee_objects = obj.addressee_objects.all()
        sender_objects = obj.sender_objects.all()
        postal_objects = list(addressee_objects) + list(sender_objects)

        return [
            {
                "sender_name__first_name": postal_object.sender_name.first_name,
                "sender_name__last_name": postal_object.sender_name.last_name,
                "addressee_name__first_name": postal_object.addressee_name.first_name,
                "addressee_name__last_name": postal_object.addressee_name.last_name,
                "date_of_correspondence": postal_object.date_of_correspondence,
                "return_to_sender": postal_object.return_to_sender,
                "date_returned": postal_object.date_returned,
                "reasonreturn": postal_object.reason_for_return_original,
                "letter_enclosed": postal_object.letter_enclosed,
                "regime_censor": postal_object.regime_censor,
                "public_notes": postal_object.public_notes,
                "images": ImageSerializer(postal_object.images.all(), many=True).data,
            }
            for postal_object in postal_objects
        ]

    # def get_associated_postal_objects(self, obj):
    #     associated_objects = Object.objects.filter(
    #         Q(sender_name=obj) | Q(addressee_name=obj)
    #     )
    #     return AssociatedObjectsSerializer(associated_objects, many=True).data

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


class PostalObjectSerializer(serializers.HyperlinkedModelSerializer):
    sender_name = PersonsSerializer()
    addressee_name = PersonsSerializer()
    postmark = PostmarksSerializer(many=True)
    censored = serializers.ReadOnlyField(source="regime_censor.censor_name")
    letter_enclosed = serializers.ReadOnlyField()
    images = ImageSerializer(many=True)
    date_of_correspondence = serializers.ReadOnlyField()
    notes = serializers.ReadOnlyField(source="public_notes")
    latitude = serializers.ReadOnlyField(source="sender_name.location.latitude")
    longitude = serializers.ReadOnlyField(source="sender_name.location.longitude")
    route = serializers.SerializerMethodField()

    class Meta:
        model = Object
        fields = (
            "sender_name",
            "addressee_name",
            "postmark",
            "censored",
            "letter_enclosed",
            "images",
            "date_of_correspondence",
            "notes",
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
router.register(r"locations", LocationViewSet)
