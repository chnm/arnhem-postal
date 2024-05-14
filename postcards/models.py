import logging

# import settings
from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from taggit_selectize.managers import TaggableManager

logger = logging.getLogger(__name__)


class Image(models.Model):
    """The image of an object, photograph, or historical source. The Image model
    has a foreign key relationship with the Object model, and each Object object
    can have multiple Image objects associated with it."""

    image_id = models.BigAutoField(primary_key=True, verbose_name="Image ID")
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    image_caption = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    postcard = models.ForeignKey(
        "Object",
        on_delete=models.SET_NULL,
        related_name="images",
        null=True,
        blank=True,
    )
    primary_source = models.ForeignKey(
        "PrimarySource",
        on_delete=models.SET_NULL,
        related_name="images",
        null=True,
        blank=True,
    )

    def __str__(self):
        return str(self.image_id)

    def image_preview(self):
        if self.image:
            return mark_safe(
                '<img src="%s" style="width:100px; height:100px;" />' % self.image.url
            )
        else:
            return "No image attached"


class LanguageManager(models.Manager):
    """Manager for Language model."""

    def get_by_natural_key(self, language):
        """natural key"""
        return self.get(language=language)


class Language(models.Model):
    """Language of a transcription."""

    language = models.CharField(max_length=55, blank=True)
    display_name = models.CharField(
        max_length=255,
        blank=True,
        unique=True,
        null=True,
    )
    iso_code = models.CharField(
        max_length=3,
        blank=True,
        help_text="ISO 639 code for this language (2 or 3 letters)",
    )

    objects = LanguageManager()

    def __str__(self):
        return self.language

    def natural_key(self):
        """natural key"""
        return self.language

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        ordering = ["language"]
        constraints = [
            models.UniqueConstraint(
                fields=["language", "display_name"], name="unique_language_display_name"
            )
        ]


class Collection(models.Model):
    """A collection is the owner of a postal object (e.g., Tim Gale)"""

    collection_id = models.BigAutoField(primary_key=True, verbose_name="Collection ID")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Person(models.Model):
    ENTITY_TYPES = (
        ("person", "Person"),
        ("organization", "Organization"),
    )

    person_id = models.BigAutoField(primary_key=True)
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_TYPES,
        default="person",
        help_text="If this is an organization or some other non-person entity, select the appropriate type.",
    )
    title = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    first_name_unknown = models.BooleanField(
        default=False,
        verbose_name="First name unknown",
        help_text="Check this box if the first name is unknown.",
    )
    first_name_unclear = models.BooleanField(
        default=False,
        verbose_name="First name unclear",
        help_text="Check this box if the first name is unclear or illegible.",
    )
    last_name = models.CharField(max_length=255, null=True, blank=True)
    last_name_unknown = models.BooleanField(
        default=False,
        verbose_name="Last name unknown",
        help_text="Check this box if the last name is unknown.",
    )
    last_name_unclear = models.BooleanField(
        default=False,
        verbose_name="Last name unclear",
        help_text="Check this box if the last name is unclear or illegible.",
    )
    entity_name = models.CharField(max_length=450, null=True, blank=True)
    house_number = models.CharField(max_length=50, null=True, blank=True)
    street = models.CharField(max_length=255, null=True, blank=True)
    location = models.ForeignKey(
        "Location", on_delete=models.CASCADE, blank=True, null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_death = models.DateField(blank=True, null=True)
    latitude = models.DecimalField(
        blank=True,
        null=True,
        max_digits=9,
        decimal_places=6,
        help_text="This will be auto-generated if left empty.",
    )
    longitude = models.DecimalField(
        blank=True,
        null=True,
        max_digits=9,
        decimal_places=6,
        help_text="This will be auto-generated if left empty.",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.first_name is None and self.last_name is None and self.entity_name:
            return self.entity_name
        elif self.first_name and self.last_name and self.entity_name:
            return f"{self.first_name} {self.last_name} ({self.entity_name})"
        elif self.first_name and self.last_name:
            return self.first_name + " " + self.last_name
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return "No name provided"

    # Sort alphabetically by last name
    class Meta:
        ordering = ["last_name"]
        verbose_name = "Entities or Person"

    def get_associated_images(self):
        images = []
        for obj in Object.objects.all():
            if (
                obj.sender_name == self.person_id
                or obj.addressee_name == self.person_id
            ):
                images.append(obj.images)
        return images

    # On save, the following tries to derive the latlon from the town_city and country
    # fields. If successful, it stores the latlon in the latlon field.
    def save(self, *args, **kwargs):
        if self.latitude is None or self.longitude is None:
            try:
                from geopy.geocoders import Nominatim

                geolocator = Nominatim(user_agent="postcards")
                location_components = [
                    self.house_number,
                    self.street,
                    self.location.town_city,
                    self.location.country,
                ]
                location_string = " ".join(filter(None, location_components))
                location = geolocator.geocode(location_string)
                logger.info(f"Geocoding: {location_string}")

                if location is not None:
                    self.latitude = str(location.latitude)
                    self.longitude = str(location.longitude)
            except Exception as e:
                logger.warning("Warning in geocoding a Person: " + str(e) + str(self))
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
        town_city = self.town_city if self.town_city else "Unknown town/city"
        country = self.country if self.country else "Unknown country"
        return town_city + ", " + country

    # Return the city name string.
    def get_city_names(self):
        return self.town_city

    # Return the state/province string.
    def get_state_names(self):
        return self.province_state

    # Return the country string.
    def get_country_names(self):
        return self.country

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
                location_components = [self.town_city, self.country]
                location_string = ", ".join(filter(None, location_components))
                location = geolocator.geocode(location_string)

                self.latitude = str(location.latitude)
                self.longitude = str(location.longitude)
            except Exception as e:
                logger.warning("Warning in geocoding: " + str(e))
        super().save(*args, **kwargs)


class Postmark(models.Model):
    """
    A Postmark can contain multiple Dates and Locations,
    so we create a separate model for it.
    """

    postmark_id = models.BigAutoField(primary_key=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField(
        null=True,
        blank=True,
        help_text="Insert the date as YYYY-MM-DD or use the date picker. Leave blank if unknown.",
    )
    ordered_by_arrival = models.IntegerField(
        null=True,
        blank=True,
        help_text="If there are multiple postmarks, indicate the order by arrival (1, 2, 3, etc.).",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        location_parts = []

        if self.location.town_city:
            location_parts.append(self.location.town_city)

        if self.location.country:
            location_parts.append(self.location.country)

        location_string = ", ".join(location_parts)
        date_string = self.date.strftime("%b. %d, %Y") if self.date else "unknown date"

        return f"Postmarked at {location_string}, dated {date_string}"


class ReasonReturnManager(models.Manager):
    def get_by_natural_key(self, collection):
        return self.get(collection=collection)


class ReasonReturn(models.Model):
    id = models.BigAutoField(primary_key=True)
    language = models.ManyToManyField(
        Language, blank=True, help_text="Select the language of this return."
    )
    postal_object = models.ForeignKey(
        "Object",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="Link a document to the reason for return.",
    )
    text = models.TextField(
        blank=True, null=True, help_text="Notes on the reason for return."
    )
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    manager = ReasonReturnManager()

    class Meta:
        ordering = ["created"]


class TranscriptionManager(models.Manager):
    def get_by_natural_key(self, collection):
        return self.get(collection=collection)


class Transcription(models.Model):
    transcription_id = models.BigAutoField(primary_key=True)
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        default=1,
        null=True,
        blank=True,
        help_text="Select the language of this transcription",
    )
    postal_object = models.ForeignKey(
        "Object",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="transcriptions",
        help_text="Link a document to the transcription.",
    )
    transcription = models.TextField(
        blank=True,
        null=True,
        help_text="Transcription of the document",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    manager = TranscriptionManager()

    class Meta:
        ordering = ["created"]

    def __str__(self):
        language = self.language
        if language is not None:
            return str(language.language)
        else:
            return "No language selected"


class Censor(models.Model):
    censor_id = models.BigAutoField(primary_key=True)
    censor_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="The name of the censor location.",
    )
    censor_description = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text="A brief description of the censor if needed.",
    )
    censor_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="The location of the censor.",
    )
    censor_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes on the censor.",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.censor_name


class Object(models.Model):
    """
    The Object model is the workhorse. It handles all postal objects including postcards, letters,
    and envelopes. It has a foreign key relationship with the Person model,
    which allows us to link a sender and an addressee to the postal object.

    The Object model also has a foreign key relationship with the Collection
    model, which allows us to link a postal object to a collection so we can keep
    a controlled vocabulary of collections.
    """

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
        ("folded card", "Folded Card"),
        ("envelope printed matter", "Envelope ('printed matter')"),
        ("letter sheet", "Letter Sheet"),
        ("giro envelope", "Giro Envelope"),
        ('envelope ("printed matter")', 'Envelope ("printed matter")'),
    )

    id = models.AutoField(primary_key=True)
    item_id = models.CharField(
        max_length=255,
        default="N/A",
        verbose_name="Item ID",
        help_text="Record the file name of the image here.",
    )
    collection = models.ForeignKey(
        Collection,
        verbose_name="collection",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    collection_location = models.CharField(
        max_length=255,
        verbose_name="collection location",
        help_text="The location in the collection (folder and box).",
    )
    postmark = models.ManyToManyField(Postmark, blank=True, verbose_name="postmark")
    check_sensitive_content = models.BooleanField(
        verbose_name="Material contains sensitive content",
        help_text="Check this box if you think this postcard contains sensitive imagery or events.",
        default=False,
    )
    letter_enclosed = models.BooleanField(
        verbose_name="Letter enclosed",
        help_text="Check this box if there is a letter enclosed.",
        default=False,
    )
    return_to_sender = models.BooleanField(
        help_text="Check the box if the postcard was returned to sender."
    )
    date_returned = models.DateField(
        null=True,
        blank=True,
        help_text="Insert the date as YYYY-MM-DD or use the date picker. Leave blank if unknown.",
    )
    reason_for_return_original = models.TextField(
        max_length=600,
        null=True,
        blank=True,
        help_text="The reason for return in the original language.",
    )
    reason_for_return_translated = models.TextField(
        max_length=600,
        null=True,
        blank=True,
        help_text="The reason for return translated to English.",
    )
    regime_censor = models.CharField(
        max_length=50,
        choices=CENSOR_CHOICES,
        help_text="Was the postal object censored?",
    )
    regime_location = models.ForeignKey(
        Censor,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        help_text="If the postal object was censored, select the censor.",
    )
    regime_censor_date = models.DateField(
        null=True,
        blank=True,
        help_text="Insert the date of the censor as YYYY-MM-DD. Leave blank if unknown.",
    )
    addressee_name = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name="addressee's name",
        related_name="addressee_objects",
        blank=True,
        null=True,
    )
    sender_name = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name="sender's name",
        related_name="sender_objects",
        blank=True,
        null=True,
    )
    letter_type = models.CharField(
        max_length=50, choices=LETTER_TYPES, blank=True, null=True
    )
    date_of_correspondence = models.DateField(
        null=True,
        blank=True,
    )
    # related_images = models.ManyToManyField(
    #     Image, blank=True, verbose_name="Related images"
    # )
    translated = models.CharField(
        max_length=50,
        choices=TRANSLATION_CHOICES,
        help_text="Has the material been translated?",
    )
    # translation = models.TextField(max_length=600, blank=True, null=True)
    # transcription = models.TextField(max_length=600, blank=True, null=True)
    other = models.CharField(
        max_length=50, choices=OTHER_CHOICES, blank=True, null=True
    )
    tags = TaggableManager(
        blank=True, related_name="tagged_document", verbose_name="Keywords"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Internal notes",
        help_text="These notes are not visible to the public.",
    )
    public_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Public notes",
        help_text="These notes are visible to the public.",
    )

    # If reviewered, record the reviewer
    reviewed_by = models.ForeignKey(
        # provide list from allauth users
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_by",
        help_text="Select the last user who reviewed this document.",
    )
    reviewed_by_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date last reviewed",
        help_text="Insert the date as YYYY-MM-DD or use the date picker.",
    )

    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="last updated", blank=False, null=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="date created", blank=False, null=False
    )

    def __str__(self):
        sender_name = f"{self.sender_name.first_name or ''} {self.sender_name.last_name or ''}".strip()
        addressee_name = f"{self.addressee_name.first_name or ''} {self.addressee_name.last_name or ''}".strip()
        date_of_correspondence = (
            self.date_of_correspondence if self.date_of_correspondence else ""
        )

        return f"{sender_name} to {addressee_name}, {date_of_correspondence}"

    @property
    def sender_full_name(self):
        if self.sender_name:
            return f"{self.sender_name.first_name} {self.sender_name.last_name}"
        return None

    @property
    def addressee_full_name(self):
        if self.addressee_name:
            return f"{self.addressee_name.first_name} {self.addressee_name.last_name}"
        return None

    def get_absolute_url(self):
        return reverse("items", kwargs={"id": self.id})

    def calculate_route(self):
        """Calculate the route between the sender and the addressee."""

        cache_key = (
            f"route_{self.sender_name.person_id}_{self.addressee_name.person_id}"
        )
        route = cache.get(cache_key)

        if route is None:
            route = []
            if self.sender_name and self.sender_name.location:
                route.append(
                    {
                        "type": "person",
                        "type_description": "sender",
                        "latitude": self.sender_name.location.latitude,
                        "longitude": self.sender_name.location.longitude,
                    }
                )

            if self.regime_location:
                route.append(
                    {
                        "type": "censor",
                        "latitude": self.regime_location.censor_location.latitude,
                        "longitude": self.regime_location.censor_location.longitude,
                    }
                )

            postmarks_sorted = self.postmark.order_by("date")
            for postmark in postmarks_sorted:
                if postmark.location:
                    route.append(
                        {
                            "type": "postmark",
                            "latitude": postmark.location.latitude,
                            "longitude": postmark.location.longitude,
                        }
                    )

            if self.addressee_name and self.addressee_name.location:
                route.append(
                    {
                        "type": "person",
                        "type_description": "addressee",
                        "latitude": self.addressee_name.location.latitude,
                        "longitude": self.addressee_name.location.longitude,
                    }
                )

            # We cache the calculation for 15 minutes
            cache.set(cache_key, route, 60 * 15)

        return route

    class Meta:
        verbose_name = "Postal Material"
        verbose_name_plural = "Postal Materials"
        ordering = ["-date_of_correspondence"]


class PrimarySource(models.Model):
    DOC_TYPE = (
        ("service record", "Service Record"),
        ("military record", "Military Record"),
        ("newspaper", "Newspaper"),
        ("certificate", "Certificate"),
        ("typed letter", "Typed Letter"),
        ("identification card", "Identification Card"),
        ("book", "Book"),
        ("loose pages", "Loose Pages"),
        ("photograph", "Photograph"),
        ("license", "License"),
        ("membership card", "Membership Card"),
        ("letter", "Letter"),
        ("letter/license", "Letter/License"),
        ("pay record", "Pay Record"),
        ("account balance", "Account Balance"),
        ("papers", "Papers"),
        ("discharge form", "Discharge Form"),
        ("pamphlet", "Pamphlet"),
        ("flyer", "Flyer"),
        ("program", "Program"),
        ("typewritten certificate", "Typewritten Certificate"),
        ("card", "Card"),
        ("identity card", "Identity Card"),
        ("booklet", "Booklet"),
        ("folded card", "Folded Card"),
        ("voucher", "Voucher"),
        ("pass", "Pass"),
        ("report", "Report"),
        ("stamps", "Stamps"),
        ("lettersheet", "Lettersheet"),
        ("other", "Other"),
        ('envelope ("printed matter")', 'Envelope ("printed matter")'),
    )

    id = models.AutoField(primary_key=True)
    item_id = models.CharField(
        default="N/A",
        max_length=255,
        help_text="Record the file name of the image here.",
    )
    document_type = models.CharField(max_length=255, choices=DOC_TYPE)
    person = models.ManyToManyField(
        Person,
        verbose_name="Person",
        related_name="person",
        help_text="Select the person(s) this document is about. If the person does not exist, click the plus and add the new person.",
        blank=True,
    )
    printer = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Printer",
        help_text="Name of the printer.",
    )
    date = models.CharField(
        null=True,
        blank=True,
    )
    is_date_known_or_precise = models.BooleanField(
        default=False,
        verbose_name="Is the date unknown or imprecise?",
        help_text="Check this box if the date is unknown or not precise.",
    )
    title = models.CharField(
        blank=True,
        null=True,
        verbose_name="Title",
        help_text="Title of the document.",
        max_length=255,
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Describe the document.",
    )
    medium = models.CharField(
        blank=True,
        null=True,
        help_text="The medium of the document.",
    )
    number_of_pages = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Number of pages",
        help_text="How many pages does the document have?",
    )
    transcription = models.TextField(
        blank=True,
        null=True,
        verbose_name="Transcription",
        help_text="Transcribe the document.",
    )
    has_document_been_translated = models.BooleanField(
        blank=True,
        null=True,
        default=False,
    )
    tags = TaggableManager(
        blank=True, related_name="tagged_source", verbose_name="Keywords"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Internal notes",
        help_text="These notes are not visible to the public.",
    )
    public_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Public notes",
        help_text="These notes are visible to the public.",
    )
    cataloger = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cataloger",
        help_text="Select the user who cataloged or indexed this document.",
    )
    date_cataloged = models.DateField(
        null=True, blank=True, help_text="Enter the date this item was cataloged."
    )
    collection = models.ForeignKey(
        Collection,
        verbose_name="collection",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    collection_location = models.CharField(
        max_length=255,
        verbose_name="collection location",
        help_text="The location in the collection (folder and box).",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="date created", blank=False, null=False
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="last updated", blank=False, null=False
    )

    def __str__(self):
        return str(self.title)

    def image_canvas(self):
        if self.file:
            return mark_safe(
                '<img src="%s" style="width:100px; height:100px;" />' % self.file.url
            )
        else:
            return "None attached"

    class Meta:
        verbose_name = "Document"
