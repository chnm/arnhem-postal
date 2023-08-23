from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from .models import Location, Person


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
        exclude = ("location_id",)

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
    # This method is for matching the location field in the Person model to the Location model.
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
