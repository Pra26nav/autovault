from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet


# ──────────────────────────────────────────────
# HOME PAGE
# ──────────────────────────────────────────────
class HomePage(Page):
    tagline = models.CharField(max_length=255, default="The Ultimate Supercar Encyclopedia")
    intro = RichTextField(blank=True)
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('tagline'),
        FieldPanel('intro'),
        FieldPanel('hero_image'),
    ]

    subpage_types = [
        'home.BrandIndexPage',
        'home.BlogIndexPage',
        'home.FounderIndexPage',
    ]

    class Meta:
        verbose_name = "Home Page"


# ──────────────────────────────────────────────
# BRAND INDEX PAGE
# ──────────────────────────────────────────────
class BrandIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    subpage_types = ['home.BrandPage']
    parent_page_types = ['home.HomePage']

    def get_context(self, request):
        context = super().get_context(request)
        context['brands'] = BrandPage.objects.live().order_by('title')
        return context

    class Meta:
        verbose_name = "Brand Index Page"


# ──────────────────────────────────────────────
# BRAND PAGE
# ──────────────────────────────────────────────
class BrandPage(Page):
    COUNTRY_CHOICES = [
        ('Italy', 'Italy'),
        ('Germany', 'Germany'),
        ('UK', 'United Kingdom'),
        ('USA', 'United States'),
        ('Sweden', 'Sweden'),
        ('France', 'France'),
        ('Czech Republic', 'Czech Republic'),
    ]

    country_of_origin = models.CharField(max_length=100, choices=COUNTRY_CHOICES)
    founded_year = models.PositiveIntegerField()
    headquarters = models.CharField(max_length=255)
    origin_story = RichTextField()
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    brand_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    tagline = models.CharField(max_length=255, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField('origin_story'),
        index.FilterField('country_of_origin'),
        index.FilterField('founded_year'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('country_of_origin'),
            FieldPanel('founded_year'),
            FieldPanel('headquarters'),
            FieldPanel('tagline'),
        ], heading="Brand Info"),
        FieldPanel('origin_story'),
        FieldPanel('logo'),
        FieldPanel('brand_image'),
    ]

    subpage_types = ['home.CarModelPage']
    parent_page_types = ['home.BrandIndexPage']

    def get_context(self, request):
        context = super().get_context(request)
        context['car_models'] = CarModelPage.objects.live().child_of(self).order_by('year_of_manufacture')
        return context

    class Meta:
        verbose_name = "Brand Page"


# ──────────────────────────────────────────────
# CAR MODEL PAGE
# ──────────────────────────────────────────────
class CarModelPage(Page):
    ENGINE_CHOICES = [
        ('V6', 'V6'),
        ('V8', 'V8'),
        ('V10', 'V10'),
        ('V12', 'V12'),
        ('W12', 'W12'),
        ('W16', 'W16'),
        ('Flat-6', 'Flat-6 (Boxer)'),
        ('Inline-6', 'Inline-6'),
        ('Straight-8', 'Straight-8'),
    ]

    year_of_manufacture = models.PositiveIntegerField()
    country_of_origin = models.CharField(max_length=100)
    engine_type = models.CharField(max_length=20, choices=ENGINE_CHOICES)
    horsepower = models.PositiveIntegerField(help_text="in bhp")
    units_produced = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Total units produced worldwide (leave blank if unlimited/ongoing)"
    )
    is_limited_edition = models.BooleanField(default=False)
    top_speed_kmh = models.PositiveIntegerField(null=True, blank=True, help_text="Top speed in km/h")
    zero_to_hundred = models.DecimalField(
        max_digits=4, decimal_places=2,
        null=True, blank=True,
        help_text="0-100 km/h in seconds"
    )
    description = RichTextField()
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.FilterField('engine_type'),
        index.FilterField('year_of_manufacture'),
        index.FilterField('horsepower'),
        index.FilterField('is_limited_edition'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('year_of_manufacture'),
            FieldPanel('country_of_origin'),
            FieldPanel('engine_type'),
            FieldPanel('horsepower'),
            FieldPanel('units_produced'),
            FieldPanel('is_limited_edition'),
            FieldPanel('top_speed_kmh'),
            FieldPanel('zero_to_hundred'),
        ], heading="Car Specifications"),
        FieldPanel('description'),
        FieldPanel('hero_image'),
    ]

    parent_page_types = ['home.BrandPage']

    class Meta:
        verbose_name = "Car Model Page"


# ──────────────────────────────────────────────
# BLOG INDEX PAGE
# ──────────────────────────────────────────────
class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    subpage_types = ['home.BlogPostPage']
    parent_page_types = ['home.HomePage']

    def get_context(self, request):
        context = super().get_context(request)
        category = request.GET.get('category', '')
        posts = BlogPostPage.objects.live().child_of(self).order_by('-date')
        if category:
            posts = posts.filter(category=category)
        context['posts'] = posts
        context['selected_category'] = category
        context['categories'] = BlogPostPage.CATEGORY_CHOICES
        return context

    class Meta:
        verbose_name = "Blog Index Page"


# ──────────────────────────────────────────────
# BLOG POST PAGE
# ──────────────────────────────────────────────
class BlogPostPage(Page):
    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('history', 'History'),
        ('reviews', 'Reviews'),
    ]

    date = models.DateField("Post date")
    author = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='news')
    intro = models.TextField(max_length=500, help_text="Short summary shown on listing page")
    body = RichTextField()
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('intro'),
        index.FilterField('category'),
        index.FilterField('date'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('author'),
            FieldPanel('category'),
        ], heading="Post Info"),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('cover_image'),
    ]

    parent_page_types = ['home.BlogIndexPage']

    class Meta:
        verbose_name = "Blog Post"


# ──────────────────────────────────────────────
# FOUNDER INDEX PAGE
# ──────────────────────────────────────────────
class FounderIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    subpage_types = ['home.FounderPage']
    parent_page_types = ['home.HomePage']

    def get_context(self, request):
        context = super().get_context(request)
        context['founders'] = FounderPage.objects.live().child_of(self).order_by('title')
        return context

    class Meta:
        verbose_name = "Founder Index Page"


# ──────────────────────────────────────────────
# FOUNDER PAGE
# ──────────────────────────────────────────────
class FounderPage(Page):
    brand_name = models.CharField(max_length=255, help_text="e.g. Ferrari, Lamborghini")
    nationality = models.CharField(max_length=100)
    birth_year = models.PositiveIntegerField()
    death_year = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank if still alive")
    legacy_quote = models.TextField(max_length=500, blank=True)
    biography = RichTextField()
    portrait = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('biography'),
        index.FilterField('nationality'),
        index.FilterField('brand_name'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('brand_name'),
            FieldPanel('nationality'),
            FieldPanel('birth_year'),
            FieldPanel('death_year'),
            FieldPanel('legacy_quote'),
        ], heading="Founder Info"),
        FieldPanel('biography'),
        FieldPanel('portrait'),
    ]

    parent_page_types = ['home.FounderIndexPage']

    class Meta:
        verbose_name = "Founder Page"
