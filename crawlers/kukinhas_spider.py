
import json
import re
import hashlib
import unicodedata

import scrapy

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class KukinhasSpider(CrawlSpider):
    name = "kukinhas"
    allowed_domains = ["kukinhas.com"]

    start_urls = [
        "https://kukinhas.com/receitas-z-recipes/"
    ]

    rules = (
        Rule(
            LinkExtractor(
                allow=(r"/\d{4}/\d{2}/",)
            ),
            callback="parse_recipe",
            follow=False,
        ),
    )

    custom_settings = {
    # já existentes
    "USER_AGENT": "RecetasGallegasBot/0.1 (+https://github.com/nathcarnevalli/recipes-search)",
    "ROBOTSTXT_OBEY": True,
    "DOWNLOAD_DELAY": 2,
    "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
    "AUTOTHROTTLE_ENABLED": True,
    "RETRY_TIMES": 5,
    "FEED_EXPORT_ENCODING": "utf-8",

    # limites do rastreio ("límites del rastreo")
    "DEPTH_LIMIT": 5,
    "DOWNLOAD_TIMEOUT": 30,
    "AUTOTHROTTLE_MAX_DELAY": 30,

    # esquema comum entre fontes (id, texto, URL, sitio de origen)
    "FEEDS": {
        "data/kukinhas.json": {
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
    "LOG_LEVEL": "INFO",
}

    def parse_recipe(self, response):
        # Obter el título de la receta
        title = response.css("h1::text").get()
        if not title:
            title = response.css("h1 ::text").get()

        title = " ".join(title.split()) if title else ""

        # Leer el texto del artículo
        raw_lines = response.css("article ::text").getall()
        lines = [
            re.sub(r"\s+", " ", line).strip()
            for line in raw_lines
            if line.strip()
        ]

        def normalize(text):
            text = unicodedata.normalize("NFKD", text)
            text = "".join(
                c for c in text
                if not unicodedata.combining(c)
            )
            return text.lower().strip()

        # Localizar las secciones de ingredientes y preparación
        ingredients = []
        preparation = []

        ingredient_start = None
        preparation_start = None

        for i, line in enumerate(lines):
            normalized = normalize(line)

            if (
                ingredient_start is None
                and normalized.startswith("ingredientes")
            ):
                ingredient_start = i + 1

            if (
                ingredient_start is not None
                and preparation_start is None
                and normalized.startswith("preparacion")
            ):
                preparation_start = i + 1
                ingredients = lines[ingredient_start - 1:i]

        if preparation_start is not None:
            for line in lines[preparation_start:]:
                normalized = normalize(line)

                # Deter a preparación antes de comezar a tradución inglesa
                if (
                    normalized == "tags"
                    or normalized.startswith("ingredients for")
                    or normalized.startswith("step by step")
                    or "cockles carino style" in normalized
                    or (len(line.strip()) >= 10 and set(line.strip()) <= {"_", "-", "—"})
                ):
                    break

                preparation.append(line)

        # Limpiar el texto de los encabezados
        ingredients = [
            re.sub(r"^[–—•-]\s*", "", x)
            for x in ingredients
            if normalize(x) not in (
                "ingredientes",
                "preparacion",
                "preparacion paso a paso",
            )
        ]

        preparation = [
            x for x in preparation
            if x.strip()
        ]

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
            "source": "Kukinhas",
        }
