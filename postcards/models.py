import logging

# import settings
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from taggit_selectize.managers import TaggableManager

logger = logging.getLogger(__name__)


class Archive(models.Model):
    """The location of the postcard in the archival collection (folder/box)"""

    location = models.CharField(max_length=255)

    def __str__(self):
        return self.location


# The Image model has a foreign key relationship with the Object model, and
# each Object object can have multiple Image objects associated with it.
class Image(models.Model):
    """The image of an object, photograph, or ancillary source"""

    image_id = models.BigAutoField(primary_key=True, verbose_name="Image ID")
    image = models.ImageField(upload_to="images/")
    image_caption = models.CharField(max_length=255)
    postcard = models.ForeignKey(
        "Object", on_delete=models.CASCADE, related_name="images", null=True
    )

    def __str__(self):
        return self.image_caption


class Collection(models.Model):
    """A collection is the owner of an object"""

    collection_id = models.BigAutoField(primary_key=True, verbose_name="Collection ID")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Person(models.Model):
    person_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    house_number = models.CharField(max_length=50, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    location = models.ForeignKey(
        "Location", on_delete=models.CASCADE, blank=True, null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_death = models.DateField(blank=True, null=True)
    latitude = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=6
    )
    longitude = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=6
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return either first name or last name, but don't throw an error if one is missing
        if self.first_name and self.last_name:
            return self.last_name + " " + self.first_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return "No name provided"

    # Sort alphabetically by last name
    class Meta:
        ordering = ["last_name"]

    # On save, the following tries to derive the latlon from the town_city and country
    # fields. If successful, it stores the latlon in the latlon field.
    def save(self, *args, **kwargs):
        if self.latitude is None or self.longitude is None:
            try:
                from geopy.geocoders import Nominatim

                geolocator = Nominatim(user_agent="postcards")
                # set location to house number, street, and the information linked in Location model
                location = geolocator.geocode(
                    self.house_number
                    + " "
                    + self.street
                    + " "
                    + self.location.town_city
                    + " "
                    + self.location.country
                )
                # log this to see if it's working
                logger.info(
                    "Geocoding: "
                    + self.house_number
                    + " "
                    + self.street
                    + " "
                    + self.location.town_city
                    + " "
                    + self.location.country
                )
                self.latitude = str(location.latitude)
                self.longitude = str(location.longitude)
            except Exception as e:
                logger.error("Error in geocoding: " + str(e))
        super().save(*args, **kwargs)


class Location(models.Model):
    location_id = models.BigAutoField(primary_key=True)
    town_city = models.CharField(
        max_length=100, verbose_name="Town/City", blank=True, null=True
    )
    province_state = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="State/Province"
    )
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=6
    )
    longitude = models.DecimalField(
        blank=True, null=True, max_digits=9, decimal_places=6
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.town_city + ", " + self.country

    # Always sort alphabetically
    class Meta:
        ordering = ["town_city"]

    def map_preview(self):
        # if lat and if lon, display a point on a map using OSM
        if self.latitude and self.longitude:
            return format_html(
                '<iframe width="100%" height="200" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://www.openstreetmap.org/export/embed.html?bbox={},{},{},{}&amp;layer=mapnik&amp;marker={}%2C{}" style="border: 1px solid black"></iframe><br/><small><a href="https://www.openstreetmap.org/#map=4/{}/{}">View Larger Map</a></small>',
                self.longitude,
                self.latitude,
                self.longitude,
                self.latitude,
                self.latitude,
                self.longitude,
                self.latitude,
                self.longitude,
                self.latitude,
            )
        else:
            return "No location data provided"

    # On save, the following tries to derive the latlon from the town_city and country
    # fields. If successful, it stores the latlon in the latlon field.
    def save(self, *args, **kwargs):
        if self.latitude is None or self.longitude is None:
            try:
                from geopy.geocoders import Nominatim

                geolocator = Nominatim(user_agent="postcards")
                location = geolocator.geocode(self.town_city + ", " + self.country)
                self.latitude = str(location.latitude)
                self.longitude = str(location.longitude)
            except Exception as e:
                logger.error("Error in geocoding: " + str(e))
        super().save(*args, **kwargs)


# A Postmark can contain multiple Dates and Locations,
# # so we create a separate model for it.
class Postmark(models.Model):
    postmark_id = models.BigAutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField(
        null=True,
        blank=True,
        help_text="Insert the date as YYYY-MM-DD or use the date picker. Leave blank if unknown.",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # TODO: Come up with a def str to return the location and date of the postmark.
    def __str__(self):
        return (
            "Postmark for "
            + self.location.town_city
            + ", "
            + self.location.country
            + ", dated "
            + str(self.date)
        )


class Object(models.Model):
    CENSOR_CHOICES = (
        ("yes", "Yes"),
        ("no", "No"),
        ("unknown", "Unknown"),
    )

    TRANSLATION_CHOICES = (
        ("yes", "Yes"),
        ("no", "No"),
        ("partial", "Partial"),
    )

    OTHER_CHOICES = (
        ("red cross", "Red Cross"),
        ("uberroller", "Uberroller"),
        ("pow", "POW"),
    )

    LETTER_TYPES = (
        ("postcard", "Postcard"),
        ("letter", "Letter"),
        ("package", "Package"),
        ("envelope", "Envelope"),
    )

    id = models.AutoField(primary_key=True)
    item_id = models.CharField(max_length=255, default="N/A", verbose_name="Item ID")
    collection = models.ManyToManyField(Collection, verbose_name="collection")
    collection_location = models.ForeignKey(
        Archive, on_delete=models.CASCADE, verbose_name="Location in the Collection"
    )
    postmark = models.ManyToManyField(Postmark, verbose_name="postmark")
    return_to_sender = models.BooleanField(
        help_text="Check the box if the postcard was returned to sender."
    )
    date_returned = models.DateField(
        null=True,
        blank=True,
        help_text="Insert the date as YYYY-MM-DD or use the date picker. Leave blank if unknown.",
    )
    reason_for_return = models.TextField(max_length=255, null=True, blank=True)
    regime_censor = models.CharField(max_length=50, choices=CENSOR_CHOICES)
    addressee_name = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name="addressee's name",
        related_name="addressee_name",
    )
    sender_name = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name="sender's name",
        related_name="sender_name",
    )
    letter_type = models.CharField(max_length=50, choices=LETTER_TYPES)
    date_of_correspondence = models.DateField()
    letter_enclosed = models.BooleanField()
    file = models.FileField(
        upload_to="files/", null=True, blank=True, verbose_name="Upload a file"
    )
    related_images = models.ManyToManyField(
        Image, blank=True, verbose_name="Related images"
    )
    translated = models.CharField(max_length=50, choices=TRANSLATION_CHOICES)
    translation = models.TextField(max_length=600, blank=True, null=True)
    transcription = models.TextField(max_length=600, blank=True, null=True)
    other = models.CharField(
        max_length=50, choices=OTHER_CHOICES, blank=True, null=True
    )
    tags = TaggableManager(
        blank=True, related_name="tagged_document", verbose_name="Keywords"
    )
    notes = models.TextField(
        max_length=600,
        blank=True,
        null=True,
        verbose_name="Internal notes",
        help_text="These notes are not visible to the public.",
    )

    check_sensative_content = models.BooleanField(
        help_text="Check this box if you think this postcard contains sensitive imagery or events.",
        default=False,
    )

    # If reviewered, record the reviewer
    reviewed_by = models.ForeignKey(
        # provide list from allauth users
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_by",
    )

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="last updated", blank=False, null=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="date created", blank=False, null=False
    )

    def __str__(self):
        # "Return the sender's name, addressee's name, and date of correspondence."
        return (
            self.sender_name.first_name
            + " "
            + self.sender_name.last_name
            + " to "
            + self.addressee_name.first_name
            + " "
            + self.addressee_name.last_name
            + ", "
            + str(self.date_of_correspondence)
        )

    def get_absolute_url(self):
        return reverse("postcard_detail", kwargs={"pk": self.pk})

    def image_canvas(self):
        if self.file:
            return mark_safe(
                '<img src="%s" style="width:100px; height:100px;" />' % self.file.url
            )
        else:
            return "None attached"

    image_canvas.short_description = "Image"
