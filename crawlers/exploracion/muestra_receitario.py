import json
import re
import scrapy

class MuestraReceitarioSpider(scrapy.Spider):
    name = "muestra_receitario"
    start_urls = ["https://receitario.gal/category/receitas-tradicionais/"]

    custom_settings = {
        "USER_AGENT": "RecetasGallegasBot/0.1 (+https://github.com/nathcarnevalli/recipes-search)",
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 2, 
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,  
        "AUTOTHROTTLE_ENABLED": True,        
        "RETRY_TIMES": 5, 
        "CLOSESPIDER_ITEMCOUNT": 10,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def parse(self, response):
        for enlace in response.css("ul.title-list li.title-list-item a::attr(href)").getall():
            yield response.follow(enlace, callback=self.parse_receta)

    def parse_receta(self, response):
        articulo = self.extraer_articulo_jsonld(response)

        yield {
            "url": response.url,
            "sitio": "receitario",
            "id_wordpress": self.extraer_postid(response),
            "titulo": response.css("h1::text").get(),
            "fecha_publicacion": articulo.get("datePublished"),
            "categorias": self.como_lista(articulo.get("articleSection")),
            "etiquetas": self.como_lista(articulo.get("keywords")),
            "lineas": self.extraer_lineas(response),
        }

    def extraer_articulo_jsonld(self, response):
        for bloque in response.css('script[type="application/ld+json"]::text').getall():
            try:
                datos = json.loads(bloque)
            except json.JSONDecodeError:
                continue
            for nodo in datos.get("@graph", []):
                if nodo.get("@type") == "Article":
                    return nodo
        return {}

    def como_lista(self, valor):
        if not valor:
            return []
        if isinstance(valor, str):
            return [v.strip() for v in valor.split(",") if v.strip()]
        return valor

    def extraer_postid(self, response):
        clases = response.css("body::attr(class)").get() or ""
        coincidencia = re.search(r"postid-(\d+)", clases)
        return int(coincidencia.group(1)) if coincidencia else None

    def extraer_lineas(self, response):
        lineas = []
        bloques = response.css("div.entry-content").xpath(
            ".//*[self::p or self::li or self::h2 or self::h3 or self::h4]"
            "[not(ancestor::p or ancestor::li)]"
            "[not(ancestor::div[contains(@class, 'wiki-toc')])]"
        )
        for bloque in bloques:
            texto = "".join(bloque.xpath(".//text()").getall())
            for linea in texto.split("\n"):
                linea = " ".join(linea.split())
                if linea:
                    lineas.append(linea)
        return lineas