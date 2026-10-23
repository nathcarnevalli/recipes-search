import json
import re
import scrapy

class MuestraKukinhasSpider(scrapy.Spider):
    name = "muestra_kukinhas"
    allowed_domains = ["kukinhas.com"]
    start_urls = ["https://kukinhas.com/receitas-tradicionais/"]

    custom_settings = {
        "USER_AGENT": "RecetasGallegasBot/0.1 (+https://github.com/nathcarnevalli/recipes-search)",
        "ROBOTSTXT_OBEY": True,
        "DOWNLOAD_DELAY": 1,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def parse(self, response):
        for enlace in response.css("div.entry-content a::attr(href)").getall():
            if re.search(r'/\d{4}/\d{2}/', enlace):
                yield response.follow(enlace, callback=self.parse_receta)

        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_receta(self, response):
        lineas = self.extraer_lineas(response)

        if not any(l.lower().startswith("ingredient") for l in lineas):
            return

        yield {
            "url": response.url,
            "sitio": "kukinhas",
            "titulo": response.css("h1::text").get(),
            "fecha_publicacion": self.extraer_fecha(response),
            "categorias": response.css('a[rel~="category"]::text').getall(),
            "etiquetas": response.css('a[rel~="tag"]::text').getall(),
            "lineas": lineas,
        }

    def extraer_fecha(self, response):
        for bloque in response.css('script[type="application/ld+json"]::text').getall():
            try:
                datos = json.loads(bloque)
            except json.JSONDecodeError:
                continue
            for nodo in datos.get("@graph", []):
                if nodo.get("@type") == "Article":
                    return nodo.get("datePublished")
        return None

    def extraer_lineas(self, response):
        lineas = []
        bloques = response.css("div.entry-content").xpath(
            ".//*[self::p or self::li or self::h2 or self::h3 or self::h4]"
            "[not(ancestor::p or ancestor::li)]"
        )
        for bloque in bloques:
            texto = "".join(bloque.xpath(".//text()").getall())
            for linea in texto.split("\n"):
                linea = " ".join(linea.split())
                if linea:
                    lineas.append(linea)
        return lineas
