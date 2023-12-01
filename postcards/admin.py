from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils.html import format_html
from import_export.admin import ExportMixin

from .models import (
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

# Register models we haven't added custom adjustments to but still want access to in
# the admin interface.
# admin.site.register(Language)


# Custom adjustments to our admin views
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


class PostmarkInline(admin.TabularInline):
    """When looking at an individual Postcard, we want to see the Postmark and the Image.
    We can do this by adding a PostmarkInline and ImageInline to the PostcardAdmin class.
    """

    model = Postmark
    extra = 1


class PersonTabularInline(admin.TabularInline):
    model = Person
    extra = 1


class PostmarkAdmin(ExportMixin, admin.ModelAdmin):
    """We provide import/export abilities to the postmarks."""

    resource_class = PostmarkResource
    list_display = ("location", "date")


admin.site.register(Postmark, PostmarkAdmin)


class LocationAdmin(ExportMixin, admin.ModelAdmin):
    """We provide import/export abilities to the locations, as well as display the custom map widget."""

    resource_class = LocationResource
    list_per_page = 15
    list_display = ("town_city", "province_state", "country", "map_preview")
    # formfield_overrides = {models.FileField: {"widget": CustomAdminMapWidget}}


admin.site.register(Location, LocationAdmin)


class TranscriptionInline(admin.TabularInline):
    """We provide the ability for transcriptions to happen as an in-line component to the Objects"""

    model = Transcription


class ReasonReturnInline(admin.TabularInline):
    """Provide the ability for notes about the reason for a letter's return as an in-line component to the Objects"""

    model = ReasonReturn


class ImageInline(admin.StackedInline):
    model = Image
    readonly_fields = ("image_preview",)


class RelatedImagesInline(admin.StackedInline):
    model = Image
    readonly_fields = ("image_preview",)


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
        # "image_canvas",
    )
    inlines = [TranscriptionInline, ImageInline]
    search_fields = ["item_id", "sender_name", "addressee_name"]
    list_filter = (
        "collection",
        "letter_enclosed",
        "sender_name",
        "addressee_name",
        "postmark",
    )
    filter_horizontal = ("postmark",)
    extra = 1


admin.site.register(Object, ObjectAdmin)


class ObjectsInline(admin.TabularInline):
    model = Object
    extra = 1
    fk_name = "sender_name"


class PersonAdmin(ExportMixin, admin.ModelAdmin):
    """We provide the ability to import/export people."""

    list_display = (
        "last_name",
        "first_name",
        "title",
        "entity_type",
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
                    "last_name",
                ),
            },
        ),
        (
            "Entity Details",
            {
                "classes": ("collapse",),  # This makes the section collapsible
                "fields": ("entity_name",),
            },
        ),
        (
            "Location Details",
            {
                "classes": ("collapse",),  # This makes the section collapsible
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
    inlines = [ObjectsInline]


admin.site.register(Person, PersonAdmin)


class PrimarySourceAdmin(admin.ModelAdmin):
    model = PrimarySource
    list_display = ("document_type", "date", "description")
    inlines = [ImageInline]
    filter_horizontal = ("person",)


admin.site.register(PrimarySource, PrimarySourceAdmin)
