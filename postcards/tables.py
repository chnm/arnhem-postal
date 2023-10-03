import django_tables2 as tables

from postcards.models import Object


class ItemHTMxMultiColumnTable(tables.Table):
    class Meta:
        model = Object
        show_header = False
        template_name = "postcards/templates/item_col_filter.html"
