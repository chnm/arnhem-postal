import django_tables2 as tables

from postcards.models import Object


class ItemHtmxTable(tables.Table):
    item_number = tables.TemplateColumn(
        accessor="item_id", verbose_name="Item ID", template_name="postal/item_id.html"
    )
    thumbnail = tables.TemplateColumn(
        template_name="postal/thumbnail.html", orderable=False
    )
    sender_name = tables.Column(accessor="sender_name", verbose_name="Sender's name")
    addressee_name = tables.Column(
        accessor="addressee_name", verbose_name="Addressee's name"
    )
    date_of_correspondence = tables.Column()
    town_city = tables.Column(
        accessor="sender_name__location__town_city", verbose_name="City"
    )
    province_state = tables.Column(
        accessor="sender_name__location__province_state", verbose_name="Province"
    )
    postmark = tables.ManyToManyColumn(
        separator=", ", accessor="postmark", verbose_name="Postmark"
    )
    collection = tables.Column(accessor="collection", verbose_name="Collection")

    class Meta:
        model = Object
        template_name = "postal/item_table.html"
        empty_text = "No data available for the select filters."
        fields = (
            "item_number",
            "thumbnail",
            "sender_name",
            "addressee_name",
            "date_of_correspondence",
            "town_city",
            "province_state",
            "postmark",
            "collection",
        )
