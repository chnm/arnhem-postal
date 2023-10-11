from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from .models import Location, Object, Person, Postmark


class LocationResource(resources.ModelResource):
    # When we run an import, we only want to import the CSV fields town, city, and country. These
    # correspond to the model fields of town_city, province_state, and country.
    # There is no ID key in the CSV, and it's auto-incremented anyway by the model.
    # We also want to make sure that the town, state, and country fields are required.
    town_city = fields.Field(attribute="town_city", column_name="city")
    province_state = fields.Field(attribute="province_state", column_name="state")
    country = fields.Field(attribute="country", column_name="country")

    class Meta:
        model = Location
        fields = ("town_city", "province_state", "country")
        import_id_fields = ("town_city", "province_state", "country")
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True
        exclude = "location_id"

    def before_import_row(self, row, **kwargs):
        # This method is called before each row is imported. If a field is empty, we want to skip the row.
        # We do not want to raise an exception, because we want to skip the row silently.
        if not row["city"] or not row["state"] or not row["country"]:
            kwargs["skip_row"] = True
        else:
            pass

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        # This method is called before the import begins. We want to make sure that the dataset has
        # a header row. If it doesn't, we want to raise an exception.
        if not dataset.headers:
            raise Exception("The CSV file must have a header row.")
        else:
            pass

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        # This method is called after the import is complete. We want to make sure that the dataset
        # has at least one row. If it doesn't, we want to raise an exception.
        if not dataset:
            raise Exception("The CSV file must have at least one row.")
        else:
            pass

    def get_instance(self, instance_loader, row):
        # This method is called when the import is ready to create a new instance. We want to make
        # sure that the instance doesn't already exist. If it does, we want to skip the row.
        town_city = row.get("city")
        province_state = row.get("state")
        country = row.get("country")
        try:
            return self._meta.model.objects.get(
                town_city=town_city, province_state=province_state, country=country
            )
        except self._meta.model.DoesNotExist:
            return None


class LocationWidget(ForeignKeyWidget):
    # This method is for matching the location field in a model to the Location model.
    # We need to match against each of the fields in the Location model for the import
    # to work correctly.
    def get_queryset(self, value, row, *args, **kwargs):
        return self.model.objects.filter(
            town_city=row["addressee_town_city"],
            province_state=row["addressee_province_state"],
            country=row["addressee_country"],
        )

    def clean(self, value, row=None, *args, **kwargs):
        # This method is for cleaning the location field in the Person model. We need to match
        # against each of the fields in the Location model for the import to work correctly.
        try:
            return self.model.objects.get(
                town_city=row["addressee_town_city"],
                province_state=row["addressee_province_state"],
                country=row["addressee_country"],
            )
        except self.model.DoesNotExist:
            return None

    def get_export_value(self, obj):
        # This method is for exporting the location field in the Person model. We need to match
        # against each of the fields in the Location model for the import to work correctly.
        return obj.town_city + ", " + obj.province_state + ", " + obj.country


class PersonResource(resources.ModelResource):
    title = fields.Field(attribute="title", column_name="addressee_title")
    first_name = fields.Field(
        attribute="first_name", column_name="addressee_first_name"
    )
    last_name = fields.Field(attribute="last_name", column_name="addressee_last_name")
    house_number = fields.Field(
        attribute="house_number", column_name="addressee_house_number"
    )
    street = fields.Field(attribute="street", column_name="addressee_street")
    # the location field is a foreign key so we need to map to the Location model. We do this with
    # the ForeignKeyWidget, and need to match against each of the fields in the Location model.
    location = fields.Field(
        attribute="location",
        column_name="addressee_town_city",
        widget=LocationWidget(Location, "town_city"),
    )

    class Meta:
        model = Person
        fields = (
            "title",
            "first_name",
            "last_name",
            "house_number",
            "street",
            "location",
        )
        import_id_fields = (
            "title",
            "first_name",
            "last_name",
            "house_number",
            "street",
            "location",
        )
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True
        exclude = ("person_id",)

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        # This method is called before the import begins. We want to make sure that the dataset has
        # a header row. If it doesn't, we want to raise an exception.
        if not dataset.headers:
            raise Exception("The CSV file must have a header row.")
        else:
            pass

    def before_import_row(self, row, **kwargs):
        # This method is called before each row is imported. If a field is empty, we want to skip the row.
        # We do not want to raise an exception, because we want to skip the row silently.
        if (
            not row["addressee_title"]
            or not row["addressee_first_name"]
            or not row["addressee_last_name"]
            or not row["addressee_house_number"]
            or not row["addressee_street"]
            or not row["addressee_town_city"]
        ):
            kwargs["skip_row"] = True
        else:
            pass


class PostmarkWidget(ForeignKeyWidget):
    # This method is for matching the location field in the Postmark model to the Location model.
    # We need to match against each of the fields in the Postmark model for the import
    # to work correctly.
    def get_queryset(self, value, row, *args, **kwargs):
        return self.model.objects.filter(location=row["location"])

    def clean(self, value, row=None, *args, **kwargs):
        # This method is for cleaning the location field in the Postmark model. We need to match
        # against each of the fields in the Location model for the import to work correctly.
        try:
            return self.model.objects.get(location=row["location"])
        except self.model.DoesNotExist:
            return None

    def get_export_value(self, obj):
        # This method is for exporting the location field in the Person model. We need to match
        # against each of the fields in the Location model for the import to work correctly.
        return obj.location


class PostmarkResource(resources.ModelResource):
    location = fields.Field(
        attribute="location",
        column_name="location",
        widget=PostmarkWidget(Location, "town_city"),
    )
    date = fields.Field(attribute="date", column_name="date")

    class Meta:
        model = Postmark
        fields = (
            "location",
            "date",
        )
        import_id_fields = (
            "location",
            "date",
        )
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True
        exclude = ("postmark_id",)

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        # This method is called before the import begins. We want to make sure that the dataset has
        # a header row. If it doesn't, we want to raise an exception.
        if not dataset.headers:
            raise Exception("The CSV file must have a header row.")
        else:
            pass

    def before_import_row(self, row, **kwargs):
        # This method is called before each row is imported. If a field is empty, we want to skip the row.
        # We do not want to raise an exception, because we want to skip the row silently.
        if not row["location"] or not row["date"]:
            kwargs["skip_row"] = True
        else:
            pass


class ObjectResource(resources.ModelResource):
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        # This method is called before the import begins. We want to make sure that the dataset has
        # a header row. If it doesn't, we want to raise an exception.
        if not dataset.headers:
            raise Exception("The CSV file must have a header row.")
        else:
            pass

        # Now, we want to place data into the appropriate models.
        # People need to be placed into the People model.
        # Locations need to be placed into the Locations model.
        # Postmarks need to be placed into the Postmarks model.
        # Objects need to be placed into the Objects model.

        self.people = {}
        self.locations = {}
        self.postmarks = {}

        # We need to iterate through the rows in the dataset.
        for row in dataset.dict:
            # We need to check if the sender is in the people dictionary.
            # If they are, we need to get the person object from the dictionary.
            # If they are not, we need to create a new person object and add it to the dictionary.
            sender_name = row["sender_name"]
            if sender_name in self.people:
                sender = self.people[sender_name]
            else:
                sender = Person.objects.create(
                    title=row["sender_title"],
                    first_name=row["sender_first_name"],
                    last_name=row["sender_last_name"],
                    house_number=row["sender_house_number"],
                    street=row["sender_street"],
                    location=row["sender_location"],
                )
                self.people[sender_name] = sender

            # We need to check if the addressee is in the people dictionary.
            # If they are, we need to get the person object from the dictionary.
            # If they are not, we need to create a new person object and add it to the dictionary.
            addressee_name = row["addressee_name"]
            if addressee_name in self.people:
                addressee = self.people[addressee_name]
            else:
                addressee = Person.objects.create(
                    title=row["addressee_title"],
                    first_name=row["addressee_first_name"],
                    last_name=row["addressee_last_name"],
                    house_number=row["addressee_house_number"],
                    street=row["addressee_street"],
                    location=row["addressee_location"],
                )
                self.people[addressee_name] = addressee

            # We need to check if the location is in the locations dictionary.
            # If it is, we need to get the location object from the dictionary.
            # If it is not, we need to create a new location object and add it to the dictionary.
            location_name = row["location"]
            if location_name in self.locations:
                location = self.locations[location_name]
            else:
                location = Location.objects.create(
                    town_city=row["location_town_city"],
                    province_state=row["location_province_state"],
                    country=row["location_country"],
                )
                self.locations[location_name] = location

            # We need to check if the postmark is in the postmarks dictionary.
            # If it is, we need to get the postmark object from the dictionary.
            # If it is not, we need to create a new postmark object and add it to the dictionary.
            postmark_name = row["postmark"]
            if postmark_name in self.postmarks:
                postmarks = self.postmarks[postmark_name]
            else:
                postmarks = Postmark.objects.create()
                self.postmarks[postmark_name] = postmarks

            # We need to check if the object is in the objects dictionary.
            # If it is, we need to get the object object from the dictionary.
            # If it is not, we need to create a new object object and add it to the dictionary.
            object_name = row["object"]
            if object_name in self.objects:
                postalitem = self.objects[object_name]
            else:
                postalitem = Object.objects.create(
                    sender_name=sender,
                    addressee_name=addressee,
                    date_of_correspondence=row["date_of_correspondence"],
                    collection=row["collection"],
                )
                self.objects[object_name] = postalitem

    class Meta:
        model = Object
        fields = (
            "sender_name",
            "addressee_name",
            "date_of_correspondence",
            "collection",
        )
        import_id_fields = (
            "sender_name",
            "addressee_name",
            "date_of_correspondence",
            "collection",
        )
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True
        exclude = ("object_id",)
