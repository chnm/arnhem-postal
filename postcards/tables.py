import django_tables2 as tables

from postcards.models import Object


class ItemHtmxTable(tables.Table):
    class Meta:
        model = Object
        template_name = "postal/item_table.html"
        fields = (
            "sender_name",
            "addressee_name",
            "date_of_correspondence",
            "collection",
        )
