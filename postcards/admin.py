from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from import_export.admin import ExportMixin

from .models import (
    Censor,
    Image,
    Location,
    Object,
    Person,
    Postmark,
    PrimarySource,
    ReasonReturn,
    Transcription,
)
from .resources import LocationResource, PersonResource, PostmarkResource

# Rename our admin panel
admin.site.site_header = "Arnhem Postal History Project"
admin.site.site_title = "Arnhem Postal History Project"
admin.site.index_title = "Arnhem Postal History Project"


# Custom adjustments to our admin views for displaying images and maps
class CustomAdminFileWidget(AdminFileWidget):
    """This custom view allows us to create a preview image in the individual Historical Source or
    Image view. If no file is attached, provide the ability to upload one. Otherwise, display the image.
    """

    def render(self, name, value, attrs=None, renderer=None):
        if value:
            result = []
            result.append(
                f"""<a href="{value.url}" target="_blank">
                      <img 
                        src="{value.url}" alt="{value}" 
                        width="500" height="500"
                        style="object-fit: cover;"
                      />
                    </a>"""
            )
            result.append(super().render(name, value, attrs, renderer))
            return format_html("".join(result))
        else:
            return super().render(name, None, attrs=attrs, renderer=renderer)


class CustomAdminMapWidget(AdminFileWidget):
    """This provides an embedded map view showing the point on the lat/lon of the data using OSM that we
    display in the individual Location view"""

    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if hasattr(value, "url"):
            result.append(
                f"""<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="{value.url}" style="border: 1px solid black"></iframe><br/><small><a href="{value.url}">View Larger Map</a></small>"""
            )
        result.append(super().render(name, value, attrs, renderer))
        return format_html("".join(result))


# Set up for admin inlines ---------------------------------------------


class ImageInline(admin.StackedInline):
    model = Image
    readonly_fields = ("image_preview",)


class ObjectsInline(admin.TabularInline):
    model = Object
    extra = 1
    fk_name = "sender_name"


class PostmarkInline(admin.TabularInline):
    """When looking at an individual Postcard, we want to see the Postmark and the Image.
    We can do this by adding a PostmarkInline and ImageInline to the PostcardAdmin class.
    """

    model = Postmark
    extra = 1


class PersonTabularInline(admin.TabularInline):
    model = Person
    extra = 1


class RelatedImagesInline(admin.StackedInline):
    model = Image
    readonly_fields = ("image_preview",)


class ReasonReturnInline(admin.TabularInline):
    """Provide the ability for notes about the reason for a letter's return as an in-line component to the Objects"""

    model = ReasonReturn


class TranscriptionInline(admin.TabularInline):
    """We provide the ability for transcriptions to happen as an in-line component to the Objects"""

    model = Transcription


# Set up for admin classes ---------------------------------------------
class ImageAdmin(admin.ModelAdmin):
    list_display = ("image_id", "image_thumbnail", "image_caption", "url_to_object")

    def image_thumbnail(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.image.url)

    image_thumbnail.short_description = "Image Thumbnail"

    def url_to_object(self, obj):
        url = reverse("admin:postcards_object_change", args=[obj.postcard.id])
        return format_html('<a href="{}">{}</a>', url, obj.postcard.item_id)

    url_to_object.short_description = (
        "View the postal object associated with this image"
    )


class LocationAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = LocationResource
    list_per_page = 15
    list_display = ("country", "town_city", "province_state", "map_preview")
    list_filter = ("country", "town_city", "province_state")

    class Meta:
        model = Location
        fields = ("country", "town_city", "province_state", "latitude", "longitude")


class ObjectAdmin(ExportMixin, admin.ModelAdmin):
    """We provide import/export abilities to the objects, as well as the inline transcriptions for
    the objects."""

    model = Object.item_id

    list_display = (
        "item_id",
        "sender_name",
        "addressee_name",
        "date_of_correspondence",
        "collection_location",
        "letter_enclosed",
        "translated",
    )
    inlines = [TranscriptionInline, ImageInline]
    search_fields = ["item_id", "sender_name", "addressee_name"]
    list_filter = (
        "collection",
        "letter_enclosed",
        "sender_name",
        "addressee_name",
        "postmark",
        "date_of_correspondence",
        "regime_censor",
        "regime_location",
    )
    filter_horizontal = ("postmark",)
    extra = 1


class PersonAdmin(ExportMixin, admin.ModelAdmin):
    def view_sent_objects(self, obj):
        url = (
            reverse("admin:postcards_object_changelist")
            + "?sender_name__person_id__exact="
            + str(obj.person_id)
        )
        return format_html('<a href="{}">View sent postal items</a>', url)

    def view_received_objects(self, obj):
        url = (
            reverse("admin:postcards_object_changelist")
            + "?addressee_name__person_id__exact="
            + str(obj.person_id)
        )
        return format_html('<a href="{}">View recieved postal items</a>', url)

    list_display = (
        "last_name",
        "first_name",
        "title",
        "entity_type",
        "view_sent_objects",
        "view_received_objects",
    )
    list_filter = (
        "entity_type",
        "title",
        "location",
        "last_name",
    )
    fieldsets = (
        (
            "Entity Type",
            {
                "fields": ("entity_type",),
            },
        ),
        (
            "Person Details",
            {
                "classes": ("collapse",),
                "fields": (
                    "title",
                    "first_name",
                    (
                        "first_name_unknown",
                        "first_name_unclear",
                    ),
                    "last_name",
                    (
                        "last_name_unknown",
                        "last_name_unclear",
                    ),
                ),
            },
        ),
        (
            "Entity Details",
            {
                "classes": ("collapse",),
                "fields": ("entity_name",),
            },
        ),
        (
            "Location Details",
            {
                "classes": ("collapse",),
                "fields": (
                    "house_number",
                    "street",
                    "location",
                    "latitude",
                    "longitude",
                ),
            },
        ),
    )
    resource_class = PersonResource
    search_fields = ["first_name", "last_name"]


class PostmarkAdmin(ExportMixin, admin.ModelAdmin):
    """We provide import/export abilities to the postmarks."""

    resource_class = PostmarkResource
    list_display = ("location", "date")


class PrimarySourceAdmin(admin.ModelAdmin):
    model = PrimarySource
    list_display = ("document_type", "date", "description")
    filter_horizontal = ("person",)


# Register our models with the admin panel ---------------------------------------------
admin.site.register(Image, ImageAdmin)
admin.site.register(Censor)
admin.site.register(Person, PersonAdmin)
admin.site.register(PrimarySource, PrimarySourceAdmin)
admin.site.register(Object, ObjectAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Postmark, PostmarkAdmin)
