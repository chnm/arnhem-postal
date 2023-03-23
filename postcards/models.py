from django.db import models


class Image(models.Model):
    id = models.BigAutoField(primary_key=True)
    image = models.ImageField(upload_to='images/')
    image_caption = models.CharField(max_length=255)


class Person(models.Model):
    id = models.BigAutoField(primary_key=True)
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


class Location(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()


class Type(models.Model):
    TYPE_CHOICES = (
        ('envelope', 'Envelope'),
        ('postcard', 'Postcard'),
        ('letter form', 'Letter Form'),
        ('newsprint', 'Newsprint'),
        ('other', 'Other'),
    )
    id = models.BigAutoField(primary_key=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)


class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    tag = models.CharField(max_length=50)


class Postcard(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    item_number = models.IntegerField()

    postmark_1_date = models.DateField()
    postmark_1_location = models.CharField(max_length=50)
    postmark_2_date = models.DateField()
    postmark_2_location = models.CharField(max_length=50)

    return_to_sender = models.BooleanField()
    date_returned = models.DateField(null=True, blank=True)
    reason_for_return = models.CharField(max_length=255, null=True, blank=True)

    regime_censor = models.BooleanField()
    addressee_name = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="addressee's name",
                                       related_name="addressee_name")
    sender_name = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="sender's name",
                                    related_name="sender_name")
    type = models.ForeignKey(Type, on_delete=models.CASCADE, verbose_name="type of artifact")
    date_of_correspondence = models.DateField()
    letter_enclosed = models.BooleanField()
    translated = models.BooleanField()
    other = models.CharField(max_length=50)
    tags = models.ManyToManyField(Tag, verbose_name="tags")
    notes = models.TextField(max_length=255)
    image = models.ManyToManyField(Image, verbose_name="image")

    def __str__(self):
        return self.title
