from import_export import fields, resources

from .models import Location


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
