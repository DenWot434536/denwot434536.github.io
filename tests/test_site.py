import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import unquote, urljoin, urlparse
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://denwot434536.github.io"
RECIPES = json.loads((ROOT / "data/recipes.json").read_text(encoding="utf-8"))


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.references = []
        self.heading_count = 0
        self.images_without_alt = []
        self.ld_json = []
        self._in_ld = False
        self._ld_text = []
        self.cards = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "h1":
            self.heading_count += 1
        if tag == "img" and "alt" not in attrs:
            self.images_without_alt.append(attrs.get("src"))
        if tag in ("a", "link") and attrs.get("href"):
            self.references.append(attrs["href"])
        if tag in ("img", "script") and attrs.get("src"):
            self.references.append(attrs["src"])
        if tag == "article" and "data-recipe-card" in attrs:
            self.cards += 1
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._in_ld = True
            self._ld_text = []

    def handle_data(self, data):
        if self._in_ld:
            self._ld_text.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_ld:
            self.ld_json.append(json.loads("".join(self._ld_text)))
            self._in_ld = False


def parse(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = [ROOT / "index.html", ROOT / "about.html", ROOT / "privacy.html"]
        cls.pages += [ROOT / "recipes" / (recipe["slug"] + ".html") for recipe in RECIPES]
        cls.parsed = {path: parse(path) for path in cls.pages}

    def test_unique_recipes_have_content_and_images(self):
        self.assertEqual(len({r["slug"] for r in RECIPES}), len(RECIPES))
        for recipe in RECIPES:
            with self.subTest(recipe=recipe["slug"]):
                self.assertTrue(recipe["ingredients"])
                self.assertTrue(recipe["steps"])
                self.assertTrue((ROOT / "assets/images" / recipe["image"]).is_file())
        self.assertEqual(self.parsed[ROOT / "index.html"].cards, len(RECIPES))

    def test_local_links_and_fragments_resolve(self):
        for page, parsed in self.parsed.items():
            page_url = BASE + "/" + page.relative_to(ROOT).as_posix()
            for reference in parsed.references:
                url = urlparse(urljoin(page_url, reference))
                if url.netloc != urlparse(BASE).netloc:
                    continue
                path = unquote(url.path).lstrip("/") or "index.html"
                target = (ROOT / path).resolve()
                with self.subTest(page=page.name, reference=reference):
                    self.assertTrue(target.is_relative_to(ROOT) and target.is_file(), f"Missing {target}")
                    if url.fragment:
                        target_page = self.parsed.get(target) or parse(target)
                        self.assertIn(url.fragment, target_page.ids)

    def test_pages_have_one_main_heading_and_accessible_images(self):
        for page, parsed in self.parsed.items():
            with self.subTest(page=page.name):
                self.assertEqual(parsed.heading_count, 1)
                self.assertEqual(parsed.images_without_alt, [])

    def test_recipe_structured_data(self):
        for recipe in RECIPES:
            page = ROOT / "recipes" / (recipe["slug"] + ".html")
            with self.subTest(recipe=recipe["slug"]):
                data = self.parsed[page].ld_json
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]["@type"], "Recipe")
                self.assertEqual(data[0]["recipeIngredient"], recipe["ingredients"])
                self.assertEqual(len(data[0]["recipeInstructions"]), len(recipe["steps"]))

    def test_sitemap_contains_all_pages(self):
        root = ElementTree.parse(ROOT / "sitemap.xml").getroot()
        urls = {element.text for element in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        expected = {BASE + "/", BASE + "/about.html", BASE + "/privacy.html"}
        expected.update(BASE + "/recipes/" + r["slug"] + ".html" for r in RECIPES)
        self.assertEqual(urls, expected)

    def test_analytics_and_consent_are_available_on_every_page(self):
        for page, parsed in self.parsed.items():
            with self.subTest(page=page.name):
                self.assertIn("consent-banner", parsed.ids)
                self.assertEqual(sum(ref.endswith("assets/js/analytics.js") for ref in parsed.references), 1)
                markup = page.read_text(encoding="utf-8")
                self.assertIn("data-consent-accept", markup)
                self.assertIn("data-consent-deny", markup)
                self.assertIn("data-consent-open", markup)
                # A no-JS tracking pixel would bypass the visitor's choice.
                self.assertNotIn("mc.yandex.ru/watch/", markup)

    def test_privacy_page_describes_the_counter(self):
        privacy = (ROOT / "privacy.html").read_text(encoding="utf-8")
        self.assertIn("Яндекс Метрика", privacy)
        self.assertIn("Вебвизор", privacy)
        self.assertIn("До вашего разрешения код Метрики не загружается", privacy)
        self.assertNotIn("не подключает рекламные сети или системы аналитики", privacy)
        self.assertIn("113844022", (ROOT / "assets/js/analytics.js").read_text(encoding="utf-8"))

    def test_existing_yandex_verification_is_preserved(self):
        self.assertIn("Verification: f4b4cc3b4aabe9d9", (ROOT / "yandex_f4b4cc3b4aabe9d9.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
