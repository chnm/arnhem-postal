import django_tables2 as tables

from postcards.models import Object


class ObjectHTMxMultiColumnTable(tables.Table):
    # TODO: not working
    def sort_column(self, column, direction):
        pass

    # TODO: not working
    def get_row_attrs(self, record):
        return {
            "hx-get": reverse("object", args=[record.pk]),
            "hx-trigger": "click",
        }

    class Meta:
        model = Object
        template_name = "postal/bootstrap_htmx.html"
        fields = (
            "addressee_name",
            "sender_name",
            "date_of_correspondence",
            "collection",
        )
