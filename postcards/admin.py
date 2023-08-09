from django.contrib import admin
from django.utils.html import format_html

from .models import Archive, Collection, Image, Location, Object, Person, Postmark

admin.site.register(Person)
admin.site.register(Location)
admin.site.register(Postmark)
admin.site.register(Archive)
admin.site.register(Collection)


class ObjectAdmin(admin.ModelAdmin):
    list_display = (
        "date_of_correspondence",
        "sender_name",
        "addressee_name",
        "collection_location",
        "letter_enclosed",
    )
    search_fields = ["item_number", "sender_name", "addressee_name"]
    model = Object.item_id
    extra = 1


admin.site.register(Object, ObjectAdmin)


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
