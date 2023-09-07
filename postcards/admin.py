from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.utils.html import format_html
from import_export.admin import ImportExportMixin

from .models import Archive, Collection, Image, Location, Object, Person, Postmark
from .resources import LocationResource, PersonResource, PostmarkResource

admin.site.register(Archive)
admin.site.register(Collection)


class CustomAdminFileWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if hasattr(value, "url"):
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


class CustomAdminMapWidget(AdminFileWidget):
    """This provides an embedded map view showing the point on the lat/lon of the data using OSM"""

    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if hasattr(value, "url"):
            result.append(
                f"""<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="{value.url}" style="border: 1px solid black"></iframe><br/><small><a href="{value.url}">View Larger Map</a></small>"""
            )
        result.append(super().render(name, value, attrs, renderer))
        return format_html("".join(result))


class PostmarkAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = PostmarkResource
    list_display = ("location", "date")


admin.site.register(Postmark, PostmarkAdmin)


class LocationAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = LocationResource
    list_display = ("town_city", "province_state", "country", "map_preview")
    formfield_overrides = {models.FileField: {"widget": CustomAdminMapWidget}}


admin.site.register(Location, LocationAdmin)


class ObjectAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "date_of_correspondence",
        "sender_name",
        "addressee_name",
        "collection_location",
        "letter_enclosed",
        "image_canvas",
    )
    search_fields = ["item_number", "sender_name", "addressee_name"]
    model = Object.item_id
    formfield_overrides = {models.FileField: {"widget": CustomAdminFileWidget}}
    extra = 1


admin.site.register(Object, ObjectAdmin)


class PersonAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "title",
        "location",
    )
    resource_class = PersonResource
    search_fields = ["first_name", "last_name"]


admin.site.register(Person, PersonAdmin)


# Display images in the admin interface
# https://stackoverflow.com/questions/10390244/how-to-display-images-in-django-admin
class ImageInline(admin.ModelAdmin):
    @admin.display(description="Image")
    def image_tag(self, obj):
        return format_html(
            '<img src="{}" style="max-width:200px; max-height:200px"/>'.format(
                obj.image.url
            )
        )

    list_display = ["image_id", "image_tag", "image_caption"]


admin.site.register(Image, ImageInline)


# When looking at an individual Postcard, we want to see the Postmark and the Image.
# We can do this by adding a PostmarkInline and ImageInline to the PostcardAdmin class.
class PostmarkInline(admin.TabularInline):
    model = Postmark
    extra = 1
