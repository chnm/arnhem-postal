from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index


class ExhibitPage(Page):
    # Database fields

    body = RichTextField()
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Search index configuration

    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.FilterField("date"),
    ]

    # Editor panels configuration

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("body"),
        InlinePanel("related_links", heading="Related links", label="Related link"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        FieldPanel("feed_image"),
    ]

    # Parent page / subpage type rules

    # parent_page_types = ["exhibit.ExhibitIndex"]
    subpage_types = []


class ExhibitPageRelatedLink(Orderable):
    page = ParentalKey(
        ExhibitPage, on_delete=models.CASCADE, related_name="related_links"
    )
    name = models.CharField(max_length=255)
    url = models.URLField()

    panels = [
        FieldPanel("name"),
        FieldPanel("url"),
    ]
