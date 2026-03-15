from django.test import TestCase, Client
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import (
    HomePage,
    BrandIndexPage,
    BrandPage,
    CarModelPage,
    BlogIndexPage,
    BlogPostPage,
    FounderIndexPage,
    FounderPage,
)
import datetime


class AutoVaultTestCase(WagtailPageTestCase):

    def setUp(self):
        super().setUp()
        self.root = Page.objects.filter(depth=1).first()

        self.home = HomePage(
            title="AutoVault Test",
            slug="autovault-test",
            tagline="The Ultimate Supercar Encyclopedia",
        )
        self.root.add_child(instance=self.home)

        self.brand_index = BrandIndexPage(
            title="Brands Test",
            slug="brands-test",
            intro="All legendary brands.",
        )
        self.home.add_child(instance=self.brand_index)

        self.ferrari = BrandPage(
            title="Ferrari Test",
            slug="ferrari-test",
            country_of_origin="Italy",
            founded_year=1939,
            headquarters="Maranello, Italy",
            origin_story="<p>The story of the Prancing Horse.</p>",
            tagline="We are the Prancing Horse",
        )
        self.brand_index.add_child(instance=self.ferrari)

        self.f40 = CarModelPage(
            title="F40 Test",
            slug="f40-test",
            year_of_manufacture=1987,
            country_of_origin="Italy",
            engine_type="V8",
            horsepower=478,
            units_produced=1311,
            is_limited_edition=True,
            top_speed_kmh=324,
            zero_to_hundred="3.80",
            description="<p>The last car Enzo approved.</p>",
        )
        self.ferrari.add_child(instance=self.f40)

        self.blog_index = BlogIndexPage(
            title="Blog Test",
            slug="blog-test",
            intro="Latest from AutoVault.",
        )
        self.home.add_child(instance=self.blog_index)

        self.post = BlogPostPage(
            title="The Ferrari F40 Story Test",
            slug="ferrari-f40-story-test",
            date=datetime.date(2024, 1, 15),
            author="AutoVault Editorial",
            category="history",
            intro="The last car Enzo ever approved.",
            body="<p>Full article body here.</p>",
        )
        self.blog_index.add_child(instance=self.post)

        self.founder_index = FounderIndexPage(
            title="Founders Test",
            slug="founders-test",
            intro="The visionaries behind the legends.",
        )
        self.home.add_child(instance=self.founder_index)

        self.enzo = FounderPage(
            title="Enzo Ferrari Test",
            slug="enzo-ferrari-test",
            brand_name="Ferrari",
            nationality="Italian",
            birth_year=1898,
            death_year=1988,
            legacy_quote="I have always held that horsepower sells cars.",
            biography="<p>Enzo Ferrari founded the Prancing Horse.</p>",
        )
        self.founder_index.add_child(instance=self.enzo)

        Site.objects.all().delete()
        Site.objects.create(
            hostname="localhost",
            port=8000,
            root_page=self.home,
            is_default_site=True,
        )
        self.client = Client()


class HomePageModelTest(AutoVaultTestCase):

    def test_homepage_created(self):
        self.assertEqual(self.home.title, "AutoVault Test")
        self.assertEqual(self.home.tagline, "The Ultimate Supercar Encyclopedia")

    def test_homepage_subpage_types(self):
        self.assertIn("home.BrandIndexPage", HomePage.subpage_types)
        self.assertIn("home.BlogIndexPage", HomePage.subpage_types)
        self.assertIn("home.FounderIndexPage", HomePage.subpage_types)


class BrandPageModelTest(AutoVaultTestCase):

    def test_brand_page_fields(self):
        self.assertEqual(self.ferrari.country_of_origin, "Italy")
        self.assertEqual(self.ferrari.founded_year, 1939)
        self.assertEqual(self.ferrari.headquarters, "Maranello, Italy")

    def test_brand_page_parent(self):
        self.assertEqual(self.ferrari.get_parent().specific, self.brand_index)

    def test_brand_page_has_car_models(self):
        car_models = CarModelPage.objects.live().child_of(self.ferrari)
        self.assertEqual(car_models.count(), 1)


class CarModelPageModelTest(AutoVaultTestCase):

    def test_car_model_fields(self):
        self.assertEqual(self.f40.engine_type, "V8")
        self.assertEqual(self.f40.horsepower, 478)
        self.assertEqual(self.f40.units_produced, 1311)
        self.assertTrue(self.f40.is_limited_edition)
        self.assertEqual(self.f40.top_speed_kmh, 324)

    def test_car_model_parent_is_brand(self):
        self.assertEqual(self.f40.get_parent().specific, self.ferrari)

    def test_car_model_year_valid(self):
        self.assertGreater(self.f40.year_of_manufacture, 1900)
        self.assertLess(self.f40.year_of_manufacture, 2100)


class BlogPageModelTest(AutoVaultTestCase):

    def test_blog_post_fields(self):
        self.assertEqual(self.post.author, "AutoVault Editorial")
        self.assertEqual(self.post.category, "history")
        self.assertEqual(self.post.date, datetime.date(2024, 1, 15))

    def test_blog_post_parent_is_index(self):
        self.assertEqual(self.post.get_parent().specific, self.blog_index)

    def test_blog_category_filter(self):
        posts = BlogPostPage.objects.live().child_of(
            self.blog_index).filter(category="history")
        self.assertEqual(posts.count(), 1)

    def test_blog_category_filter_empty(self):
        posts = BlogPostPage.objects.live().child_of(
            self.blog_index).filter(category="news")
        self.assertEqual(posts.count(), 0)


class FounderPageModelTest(AutoVaultTestCase):

    def test_founder_fields(self):
        self.assertEqual(self.enzo.brand_name, "Ferrari")
        self.assertEqual(self.enzo.nationality, "Italian")
        self.assertEqual(self.enzo.birth_year, 1898)
        self.assertEqual(self.enzo.death_year, 1988)

    def test_founder_parent_is_index(self):
        self.assertEqual(self.enzo.get_parent().specific, self.founder_index)

    def test_founder_index_has_founders(self):
        founders = FounderPage.objects.live().child_of(self.founder_index)
        self.assertEqual(founders.count(), 1)


class PageHierarchyTest(AutoVaultTestCase):

    def test_can_create_brand_under_brand_index(self):
        self.assertCanCreateAt(BrandIndexPage, BrandPage)

    def test_can_create_car_under_brand(self):
        self.assertCanCreateAt(BrandPage, CarModelPage)

    def test_can_create_blog_post_under_blog_index(self):
        self.assertCanCreateAt(BlogIndexPage, BlogPostPage)

    def test_can_create_founder_under_founder_index(self):
        self.assertCanCreateAt(FounderIndexPage, FounderPage)

    def test_cannot_create_car_under_home(self):
        self.assertCanNotCreateAt(HomePage, CarModelPage)

    def test_cannot_create_brand_under_home(self):
        self.assertCanNotCreateAt(HomePage, BrandPage)

    def test_cannot_create_blog_post_under_home(self):
        self.assertCanNotCreateAt(HomePage, BlogPostPage)

    def test_cannot_create_founder_under_brand(self):
        self.assertCanNotCreateAt(BrandPage, FounderPage)


class URLTests(AutoVaultTestCase):

    def test_homepage_returns_200(self):
        response = self.client.get(self.home.url)
        self.assertEqual(response.status_code, 200)

    def test_brands_page_returns_200(self):
        response = self.client.get(self.brand_index.url)
        self.assertEqual(response.status_code, 200)

    def test_ferrari_page_returns_200(self):
        response = self.client.get(self.ferrari.url)
        self.assertEqual(response.status_code, 200)

    def test_f40_page_returns_200(self):
        response = self.client.get(self.f40.url)
        self.assertEqual(response.status_code, 200)

    def test_blog_index_returns_200(self):
        response = self.client.get(self.blog_index.url)
        self.assertEqual(response.status_code, 200)

    def test_blog_post_returns_200(self):
        response = self.client.get(self.post.url)
        self.assertEqual(response.status_code, 200)

    def test_founders_page_returns_200(self):
        response = self.client.get(self.founder_index.url)
        self.assertEqual(response.status_code, 200)

    def test_founder_detail_returns_200(self):
        response = self.client.get(self.enzo.url)
        self.assertEqual(response.status_code, 200)

    def test_search_page_returns_200(self):
        response = self.client.get("/search/")
        self.assertEqual(response.status_code, 200)

    def test_search_with_query(self):
        response = self.client.get("/search/?q=Ferrari")
        self.assertEqual(response.status_code, 200)

    def test_search_with_engine_filter(self):
        response = self.client.get("/search/?engine=V8")
        self.assertEqual(response.status_code, 200)

    def test_search_with_hp_filter(self):
        response = self.client.get("/search/?min_hp=400&max_hp=500")
        self.assertEqual(response.status_code, 200)

    def test_invalid_url_returns_404(self):
        response = self.client.get("/this-page-does-not-exist-xyz/")
        self.assertEqual(response.status_code, 404)


class TemplateTests(AutoVaultTestCase):

    def test_homepage_uses_correct_template(self):
        response = self.client.get(self.home.url)
        self.assertTemplateUsed(response, "home/home_page.html")

    def test_brand_index_uses_correct_template(self):
        response = self.client.get(self.brand_index.url)
        self.assertTemplateUsed(response, "home/brand_index_page.html")

    def test_brand_page_uses_correct_template(self):
        response = self.client.get(self.ferrari.url)
        self.assertTemplateUsed(response, "home/brand_page.html")

    def test_car_model_uses_correct_template(self):
        response = self.client.get(self.f40.url)
        self.assertTemplateUsed(response, "home/car_model_page.html")

    def test_blog_index_uses_correct_template(self):
        response = self.client.get(self.blog_index.url)
        self.assertTemplateUsed(response, "home/blog_index_page.html")

    def test_blog_post_uses_correct_template(self):
        response = self.client.get(self.post.url)
        self.assertTemplateUsed(response, "home/blog_post_page.html")

    def test_founder_index_uses_correct_template(self):
        response = self.client.get(self.founder_index.url)
        self.assertTemplateUsed(response, "home/founder_index_page.html")

    def test_founder_page_uses_correct_template(self):
        response = self.client.get(self.enzo.url)
        self.assertTemplateUsed(response, "home/founder_page.html")


class ContentTests(AutoVaultTestCase):

    def test_homepage_contains_title(self):
        response = self.client.get(self.home.url)
        self.assertContains(response, "AutoVault")

    def test_brand_page_contains_ferrari(self):
        response = self.client.get(self.brand_index.url)
        self.assertContains(response, "Ferrari")

    def test_ferrari_page_contains_founded_year(self):
        response = self.client.get(self.ferrari.url)
        self.assertContains(response, "1939")

    def test_f40_page_contains_specs(self):
        response = self.client.get(self.f40.url)
        self.assertContains(response, "478")
        self.assertContains(response, "V8")

    def test_blog_index_contains_post(self):
        response = self.client.get(self.blog_index.url)
        self.assertContains(response, "The Ferrari F40 Story Test")

    def test_blog_post_contains_author(self):
        response = self.client.get(self.post.url)
        self.assertContains(response, "AutoVault Editorial")

    def test_founder_index_contains_enzo(self):
        response = self.client.get(self.founder_index.url)
        self.assertContains(response, "Enzo Ferrari Test")

    def test_founder_page_contains_birth_year(self):
        response = self.client.get(self.enzo.url)
        self.assertContains(response, "1898")
