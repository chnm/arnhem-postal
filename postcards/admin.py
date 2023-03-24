from django.contrib import admin
from django.utils.html import format_html
from .models import Image, Person, Location, Tag, Postcard, Postmark

admin.site.register(Person)
admin.site.register(Location)
admin.site.register(Tag)
admin.site.register(Postmark)


class PostcardAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'sender_name', 'addressee_name')
    list_filter = ['tags']
    search_fields = ['item_number', 'sender_name', 'addressee_name', 'tags']
    model = Postcard.item_id
    extra = 1

admin.site.register(Postcard, PostcardAdmin)   

# Display images in the admin interface
# https://stackoverflow.com/questions/10390244/how-to-display-images-in-django-admin
class ImageInline(admin.ModelAdmin):
    @admin.display(description='Image')
    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-width:200px; max-height:200px"/>'.format(obj.image.url))

    list_display = ['image_id','image_tag','image_caption']

admin.site.register(Image, ImageInline)

# When looking at an individual Postcard, we want to see the Postmark and the Image.
# We can do this by adding a PostmarkInline and ImageInline to the PostcardAdmin class.
class PostmarkInline(admin.TabularInline):
    model = Postmark
    extra = 1