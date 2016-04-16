from datetime import date

from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django import forms

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, \
    InlinePanel, PageChooserPanel, StreamFieldPanel

from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailforms.models import AbstractEmailForm, AbstractFormField
from wagtail.wagtailsearch import index

from wagtail.wagtailcore.blocks import TextBlock, StructBlock, StreamBlock, FieldBlock, CharBlock, RichTextBlock, RawHTMLBlock
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock



from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase



class ImageFormatChoiceBlock(FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()


# A couple of abstract classes that contain commonly used fields

class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True


# Carousel items

class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    product_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        ImageChooserPanel('product_image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        FieldPanel('description'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Video items

class VideoItem(LinkFields):
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)

    panels = [
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        FieldPanel('description'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Related links

class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True


# Product item

class ProductItem(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    caption = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    description = RichTextField()
    video = models.URLField("Embed video URL", blank=True)
    price = models.CharField(max_length=255)
    sale = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('description'),
        FieldPanel('video'),
        FieldPanel('price'),
        FieldPanel('sale'),
    ]

    def __unicode__(self):
        return self.image


# Advantage item

class AdvantageItem(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    caption = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('description'),
    ]

    def __unicode__(self):
        return self.image


# Testimonials item

class TestimonialItem(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    caption = models.CharField(max_length=255, blank=True)
    description = RichTextField()
    fb = models.URLField("Embed video URL", blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('description'),
        FieldPanel('fb'),
    ]

    def __unicode__(self):
        return self.image


# Service items

class ServicelItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    caption = models.CharField(max_length=255, blank=True)
    description = RichTextField()
    icon = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('description'),
        FieldPanel('icon'),
    ]

    class Meta:
        abstract = True


# Recipes items

class RecipeItem(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    caption = models.CharField(max_length=255, blank=True)
    description = RichTextField()
    ingredient = RichTextField(blank=True)
    video = models.URLField("Embed video URL", blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
        FieldPanel('description'),
        FieldPanel('ingredient'),
        FieldPanel('video'),
    ]

    def __unicode__(self):
        return self.image


# Home Page

class HomePageCarouselItem(Orderable, CarouselItem):
    page = ParentalKey('home.HomePage', related_name='carousel_items')


class HomePageVideoItem(Orderable, VideoItem):
    page = ParentalKey('home.HomePage', related_name='video_items')


class HomePageServiceItem(Orderable, ServicelItem):
    page = ParentalKey('home.HomePage', related_name='service_items')


class HomePageProductItem(Orderable, ProductItem):
    page = ParentalKey('home.HomePage', related_name='product_items')


class HomePageAdvantageItem(Orderable, ProductItem):
    page = ParentalKey('home.HomePage', related_name='advantage_items')


class HomePageTestimonialItem(Orderable, TestimonialItem):
    page = ParentalKey('home.HomePage', related_name='testimonial_items')


class HomePageRecipeItem(Orderable, RecipeItem):
    page = ParentalKey('home.HomePage', related_name='recipe_items')


class HomePageRelatedLink(Orderable, RelatedLink):
    page = ParentalKey('home.HomePage', related_name='related_links')


class HomePage(Page):

    class Meta:
        verbose_name = "Homepage"

HomePage.content_panels = [
    InlinePanel('carousel_items', label="Carousel items"),
    InlinePanel('video_items', label="Video items"),
    InlinePanel('service_items', label="Service items"),
    InlinePanel('product_items', label="Product items"),
    InlinePanel('advantage_items', label="Advantage items"),
    InlinePanel('testimonial_items', label="Testimonial items"),
    InlinePanel('recipe_items', label="Recipe items"),
    InlinePanel('related_links', label="Related links"),
]

HomePage.promote_panels = Page.promote_panels



