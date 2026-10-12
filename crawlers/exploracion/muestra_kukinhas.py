import json
import scrapy

class MuestraKukinhasSpider(scrapy.Spider):
    name = "muestra_kukinhas"
    start_urls = ["https://kukinhas.com/receitas-tradicionais/"]

    custom_settings = {
        "USER_AGENT": "RecetasGallegasBot/0.1 (+https://github.com/nathcarnevalli/recipes-search)",
        "ROBOTSTXT_OBEY": True,       # respetar robots.txt
        "DOWNLOAD_DELAY": 1,          # 1 segundo entre peticiones
        "CLOSESPIDER_ITEMCOUNT": 10,  
        "FEED_EXPORT_ENCODING": "utf-8",  # conservar tildes y eñes en el JSON
    }

    def parse(self, response):
        #Página índice: sigue los enlaces a recetas del contenido principal.
        for enlace in response.css("div.entry-content a::attr(href)").getall():
            yield response.follow(enlace, callback=self.parse_receta)

    def parse_receta(self, response):
        lineas = self.extraer_lineas(response)

        yield {
            "url": response.url,  # URL final, después de las redirecciones
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