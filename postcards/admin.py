from django.contrib import admin
from .models import Image, Person, Location, Type, Tag, Postcard

admin.site.register(Image)
admin.site.register(Person)
admin.site.register(Location)
admin.site.register(Type)
admin.site.register(Tag)
admin.site.register(Postcard)


class PostcardAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_number', 'postmark_1_date', 'postmark_1_location', 'postmark_2_date', 'postmark_2_location', 'return_to_sender')
    list_filter = ['postmark_1_date', 'postmark_2_date']
    search_fields = ['title', 'item_number', 'postmark_1_location', 'postmark_2_location']
    model = Postcard.title
    extra = 1
