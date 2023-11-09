from import_export import fields, resources, widgets
from import_export.widgets import DateWidget, ForeignKeyWidget

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
            town_city=row["town"],
            province_state=row["state"],
            country=row["country"],
        )

    def clean(self, value, row=None, *args, **kwargs):
        # This method is for cleaning the location field in the Person model. We need to match
        # against each of the fields in the Location model for the import to work correctly.
        try:
            return self.model.objects.get(
                town_city=row["town"],
                province_state=row["state"],
                country=row["country"],
            )
        except self.model.DoesNotExist:
            return None

    def get_export_value(self, obj):
        # This method is for exporting the location field in the Person model. We need to match
        # against each of the fields in the Location model for the import to work correctly.
        return obj.town_city + ", " + obj.province_state + ", " + obj.country


class PersonResource(resources.ModelResource):
    class Meta:
        model = Person
        import_id_fields = ("addressee_last_name", "sender_last_name")


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
    sender_first_name = fields.Field(column_name="sender_first_name")
    sender_last_name = fields.Field(column_name="sender_last_name")
    addressee_first_name = fields.Field(column_name="addressee_first_name")
    addressee_last_name = fields.Field(column_name="addressee_last_name")
    sender_title = fields.Field(column_name="sender_title")
    addressee_title = fields.Field(column_name="addressee_title")

    def before_import_row(self, row, **kwargs):
        row["item_id"] = row["item_number"].strip()
        if row["return_to_sender"] == "Yes":
            row["return_to_sender"] = True
        else:
            row["return_to_sender"] = False

        row["date_returned_to_sender"] = row["date_returned_to_sender"].strip()
        if row["date_returned_to_sender"] == "No":
            row["date_returned_to_sender"] = None
        row["date_of_correspondence"] = row["date_of_correspondence"].strip()
        if row["date_of_correspondence"] == "No":
            row["date_of_correspondence"] = None

        # Next, we set regime_censor values
        row["regime_censor"] = row["censor"].lower().strip()
        if row["censor"] == "Yes":
            row["regime_censor"] = "yes"
        elif row["censor"] == "No":
            row["regime_censor"] = "no"
        elif row["censor"] == "---":
            row["regime_censor"] = "no"
        elif not row["censor"]:
            row["regime_censor"] = "no"

        row["type_(postcard/letter/package)"] = (
            row["type_(postcard/letter/package)"].lower().strip()
        )
        row["letter_type"] = row["type_(postcard/letter/package)"]
        if not row["type_(postcard/letter/package)"]:
            row["type_(postcard/letter/package)"] = "letter"

        row["letter_enclosed"] = row["letter_enclosed_(yes/no)"].lower().strip()
        if row["letter_enclosed_(yes/no)"] == "yes":
            row["letter_enclosed"] = True
        elif row["letter_enclosed_(yes/no)"] == "no":
            row["letter_enclosed"] = False

        if row["translated"] == "Yes":
            row["translated"] = "yes"
        elif row["translated"] == "No":
            row["translated"] = "no"
        elif row["translated"] == "Unknown":
            row["translated"] = "unknown"
        else:
            row["translated"] = "yes"

        row["public_notes"] = row["notes"]
        row["collection_location"] = row["location_in_collection"].strip()
        if not row["collection_location"]:
            row["collection_location"] = "Box 1"

        # Now, we accept sender_first_name and sender_last_name. These are Foreign Keys
        # to the Person model, so we do a couple things here:
        # 1) If the name does not exist in the database, we create that Person. The Person includes their first name
        # and last name, as well as their house number, street, and location. Location is a FK to the Location
        # data and we will have to match against the Location model.
        # 2) If the name does exist, we associate the Object with that Person.
        # 3) If the name is blank, we do nothing.
        if row["sender_first_name"] or row["sender_last_name"]:
            sender_data = {
                "title": row["sender_title"],
                "first_name": row["sender_first_name"],
                "last_name": row["sender_last_name"],
                "house_number": row["sender_house_number"],
                "street": row["sender_street"],
            }
            sender_instance = Person(**sender_data)
            sender_instance.save()
            row["sender_name"] = sender_instance
        else:
            pass

        # Now we do the same for addressees
        if row["addressee_first_name"] or row["addressee_last_name"]:
            addressee_data = {
                "title": row["addressee_title"],
                "first_name": row["addressee_first_name"],
                "last_name": row["addressee_last_name"],
                "house_number": row["addressee_house_number"],
                "street": row["addressee_street"],
            }
            addressee_instance = Person(**addressee_data)
            addressee_instance.save()
            row["addressee_name"] = addressee_instance
        else:
            pass

        first_name = row.get("sender_first_name", "")
        last_name = row.get("sender_last_name", "")
        if last_name:
            row["sender_name"], created = Person.objects.get_or_create(
                last_name=last_name, first_name=first_name
            )

    def get_instance(self, instance_loader, row):
        sender_name = row.get("sender_name", None)
        addressee_name = row.get("addressee_name", None)

        if sender_name:
            # Handle potential conflicts using last_name and first_name
            sender_last_name = row.get("sender_name__last_name", "")
            sender_first_name = row.get("sender_name__first_name", "")
            sender = Person.objects.filter(
                last_name=sender_last_name, first_name=sender_first_name
            ).first()
            if sender is None:
                # Create a new Person instance if not found
                sender = Person.objects.create(
                    last_name=sender_last_name, first_name=sender_first_name
                )
            row["sender"] = sender

        if addressee_name:
            # Handle potential conflicts using last_name and first_name
            addressee_last_name = row.get("addressee_name__last_name", "")
            addressee_first_name = row.get("addressee_name__first_name", "")
            addressee = Person.objects.filter(
                last_name=addressee_last_name, first_name=addressee_first_name
            ).first()
            if addressee is None:
                # Create a new Person instance if not found
                addressee = Person.objects.create(
                    last_name=addressee_last_name, first_name=addressee_first_name
                )
            row["addressee"] = addressee

        return instance_loader.get_instance(row)

    date_of_correspondence = fields.Field(
        attribute="date_of_correspondence",
        column_name="date_of_correspondence",
        widget=DateWidget(format="%Y-%m-%d %H:%M:%S"),
    )
    date_returned = fields.Field(
        attribute="date_returned",
        column_name="date_returned_to_sender",
        widget=DateWidget(format="%Y-%m-%d %H:%M:%S"),
    )
    return_to_sender = fields.Field(
        attribute="return_to_sender",
        column_name="return_to_sender",
    )

    sender_name = fields.Field(
        column_name="sender_name",
        attribute="sender",
        widget=widgets.ForeignKeyWidget(Person, field="last_name"),
    )
    addressee_name = fields.Field(
        column_name="addressee_name",
        attribute="addressee",
        widget=widgets.ForeignKeyWidget(Person, field="last_name"),
    )

    # def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
    #     # This method is called after the import is complete. We want to make sure that the dataset
    #     # has at least one row. If it doesn't, we want to raise an exception.
    #     if not dataset:
    #         raise Exception("The CSV file must have at least one row.")
    #     else:
    #         pass

    #     # Now we link together the Object and Person by associating the sender_name and addressee_name
    #     # in the Object model with the first_name and last_name in the Person model.
    #     # We do this by iterating through the dataset and matching the sender_name and addressee_name
    #     # with the first_name and last_name in the Person model.
    #     for row in dataset.dict:
    #         # because sender_name / addressee_name is the full name of a person and first_name / last_name
    #         # is the first and last name of a person, we need to split the sender_name / addressee_name
    #         # into first_name and last_name. We do this by splitting the sender_name / addressee_name
    #         # by the space character.
    #         sender_name = row["sender_name"].split(" ")
    #         addressee_name = row["addressee_name"].split(" ")
    #         # Now we iterate through the Person model and match the first_name and last_name with the
    #         # sender_name and addressee_name. If there is a match, we associate the Object with the Person.
    #         for person in Person.objects.all():
    #             if person.first_name == sender_name[0] and person.last_name == sender_name[1]:
    #                 row["sender_name"] = person
    #             elif person.first_name == addressee_name[0] and person.last_name == addressee_name[1]:
    #                 row["addressee_name"] = person
    #             else:
    #                 pass

    # def get_instance(self, instance_loader, row):
    #     # This method is called when the import is ready to create a new instance. We want to make
    #     # sure that the instance doesn't already exist. If it does, we want to skip the row.
    #     item_id = row.get("item_id")
    #     try:
    #         return self._meta.model.objects.get(item_id=item_id)
    #     except self._meta.model.DoesNotExist:
    #         return None

    class Meta:
        model = Object
        skip_unchanged = True
        report_skipped = True
        clean_model_instances = True
        import_id_fields = (
            "item_id",
            "sender_name",
            "addressee_name",
        )
        fields = (
            "item_id",
            "collection_location",
            "date_of_correspondence",
            "date_returned",
            "letter_enclosed",
            "translated",
            "regime_censor",
            "letter_type",
            "public_notes",
        )
        exclude = (
            "id",
            "postmark",
        )
