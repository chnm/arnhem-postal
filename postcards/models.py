from django.db import models
from django.urls import reverse
from django.utils.html import format_html

import logging
logger = logging.getLogger(__name__)


class Image(models.Model):
    image_id = models.BigAutoField(primary_key=True,verbose_name='Image ID')
    image = models.ImageField(upload_to='images/')
    image_caption = models.CharField(max_length=255)

    def __str__(self):
        return self.image_caption

class Person(models.Model):
    person_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    house_number = models.CharField(max_length=50)
    street = models.CharField(max_length=255)
    town_city = models.CharField(max_length=50)
    province_state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    date_of_death = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Location(models.Model):
    location_id = models.BigAutoField(primary_key=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.city + ", " + self.country


class Tag(models.Model):
    tag_id = models.BigAutoField(primary_key=True)
    tag = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tag


# A Postmark can contain multiple Dates and Locations, 
# # so we create a separate model for it.
class Postmark(models.Model):
    postmark_id = models.BigAutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True, help_text="Insert the date as YYYY-MM-DD or use the date picker. Leave blank if unknown.")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # TODO: Come up with a def str to return the location and date of the postmark.
    def __str__(self):
        return "Postmark for " + self.location.city + ", " + self.location.country + ", dated " + str(self.date)

class Postcard(models.Model):

    CENSOR_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        ('unknown', 'Unknown'),
    )

    TRANSLATION_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
        ('partial', 'Partial'),
    )

    TYPE_CHOICES = (
        ('envelope', 'Envelope'),
        ('postcard', 'Postcard'),
        ('letter form', 'Letter Form'),
        ('newsprint', 'Newsprint'),
        ('other', 'Other'),
    )

    OTHER_CHOICES = (
        ('red cross', 'Red Cross'),
        ('uberroller', 'Uberroller'),
        ('pow', 'POW'),
    )

    postcard_id = models.AutoField(primary_key=True)
    item_id = models.CharField(max_length=255, default="N/A", verbose_name="Item ID")
    image = models.ManyToManyField(Image, verbose_name="image")

    postmark = models.ManyToManyField(Postmark, verbose_name="postmark")

    return_to_sender = models.BooleanField(help_text="Check the box if the postcard was returned to sender.")
    date_returned = models.DateField(null=True, blank=True, help_text="Insert the date as YYYY-MM-DD or use the date picker. Leave blank if unknown.")
    reason_for_return = models.TextField(max_length=255, null=True, blank=True)

    regime_censor = models.CharField(max_length=50, choices=CENSOR_CHOICES)
    addressee_name = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="addressee's name", related_name="addressee_name")
    sender_name = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="sender's name", related_name="sender_name")
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    date_of_correspondence = models.DateField()
    letter_enclosed = models.BooleanField()
    translated = models.CharField(max_length=50, choices=TRANSLATION_CHOICES)
    other = models.CharField(max_length=50, choices=OTHER_CHOICES, blank=True, null=True)
    tags = models.ManyToManyField(Tag, verbose_name="tags")
    notes = models.TextField(max_length=600)
    image = models.ManyToManyField(Image, verbose_name="image")
    check_sensative_content = models.BooleanField(help_text="Check this box if you think this postcard contains sensitive imagery or events.", default=False)

    # If reviewered, record the reviewer
    reviewed_by = models.ForeignKey('authuser.User', on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_by")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="last updated", blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="date created", blank=False, null=False)

    def __str__(self):
        return self.item_id

    def get_absolute_url(self):
        return reverse('postcard_detail', kwargs={'pk': self.pk})
