import hashlib
import unicodedata

import scrapy

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class ReceitarioSpider(CrawlSpider):
    name = "receitario"
    allowed_domains = ["receitario.gal"]

    start_urls = [
        "https://receitario.gal/category/receitas-tradicionais/"
    ]

    rules = (
        # Seguir la paginación del listado
        Rule(
            LinkExtractor(restrict_css="a.next"),
            follow=True,
        ),
        # Extraer los datos de cada receta del listado
        Rule(
            LinkExtractor(restrict_css="ul.title-list li.title-list-item"),
            callback="parse_recipe",
            follow=False,
        ),
    )

    custom_settings = {
    # já existentes
    "USER_AGENT": "RecetasGallegasBot/0.1 (+https://github.com/nathcarnevalli/recipes-search)",
    "ROBOTSTXT_OBEY": True,
    "DOWNLOAD_DELAY": 4,
    "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    "AUTOTHROTTLE_ENABLED": True,
    "RETRY_TIMES": 5,
    "FEED_EXPORT_ENCODING": "utf-8",

    # limites do rastreio ("límites del rastreo")
    "DEPTH_LIMIT": 10,
    "DOWNLOAD_TIMEOUT": 30,
    "AUTOTHROTTLE_START_DELAY": 4,
    "AUTOTHROTTLE_MAX_DELAY": 30,
    "AUTOTHROTTLE_TARGET_CONCURRENCY": 0.5,

    # esquema comum entre fontes (id, texto, URL, sitio de origen)
    "FEEDS": {
        "data/receitario.json": {
            "format": "json",
            "encoding": "utf-8",
            "indent": 2,
            "overwrite": True,
        },
    },
    "FEED_EXPORT_FIELDS": ["recipe_id", "title", "ingredients", "preparation", "url", "source"],

    # idioma e ruído
    "DEFAULT_REQUEST_HEADERS": {"Accept-Language": "gl,es;q=0.9,pt;q=0.5"},
    "COOKIES_ENABLED": False,

    # desenvolvimento
    "HTTPCACHE_ENABLED": False,
    "HTTPCACHE_IGNORE_HTTP_CODES": [429, 500, 502, 503, 504],
    "LOG_LEVEL": "INFO",
}

    def parse_recipe(self, response):
        # Obter el título de la receta
        title = response.css("h1::text").get()
        if not title:
            title = response.css("h1 ::text").get()

        title = " ".join(title.split()) if title else ""

        def normalize(text):
            text = unicodedata.normalize("NFKD", text)
            text = "".join(
                c for c in text
                if not unicodedata.combining(c)
            )
            return text.lower().strip()

        # Recorrer el contenido y repartir cada línea según el <h2> que la precede
        ingredients = []
        preparation = []
        section = None

        blocks = response.css("div.entry-content").xpath(
            ".//*[self::h2 or self::h3 or self::h4 or self::p or self::li]"
            "[not(ancestor::p or ancestor::li)]"
            "[not(ancestor::div[contains(@class, 'wiki-toc')])]"
        )

        for block in blocks:
            tag = block.root.tag
            text = " ".join("".join(block.xpath(".//text()").getall()).split())

            if not text:
                continue

            if tag == "h2":
                normalized = normalize(text)

                if normalized.startswith("ingredientes"):
                    section = "ingredients"
                elif normalized.startswith(("preparacion", "elaboracion")):
                    section = "preparation"
                else:
                    section = None
            elif tag in ("h3", "h4"):
                continue
            elif section == "ingredients":
                ingredients.append(text)
            elif section == "preparation":
                preparation.append(text)

        # No guardar páginas si faltan datos esenciales
        if not title or not ingredients or not preparation:
            self.logger.warning(
                "Revisar extracción: %s | título=%s, ingredientes=%s, preparación=%s",
                response.url,
                bool(title),
                len(ingredients),
                len(preparation),
            )
            return

        # Identificador estable para evitar duplicados
        recipe_id = hashlib.sha1(
            response.url.encode("utf-8")
        ).hexdigest()[:16]

        yield {
            "recipe_id": recipe_id,
            "title": title,
            "ingredients": ingredients,
            "preparation": " ".join(preparation),
            "url": response.url,
            "source": "Receitario",
        }
