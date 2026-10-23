import argparse
import json
import subprocess
import sys

from scrapy.crawler import CrawlerProcess

from crawlers.kukinhas_spider import KukinhasSpider
from crawlers.receitario_spider import ReceitarioSpider

DATA_FILES = ["data/kukinhas.json", "data/receitario.json"]


def crawl():
    # Los dos sitios son dominios distintos: se rastrean a la vez,
    # cada spider con su propio ritmo (1 petición por dominio)
    process = CrawlerProcess()
    process.crawl(KukinhasSpider)
    process.crawl(ReceitarioSpider)
    process.start()


def check_data():
    # Un rastreo interrumpido deja el JSON vacío o incompleto
    for path in DATA_FILES:
        try:
            with open(path, encoding="utf-8") as f:
                recipes = json.load(f)
        except (OSError, json.JSONDecodeError) as error:
            raise SystemExit(f"{path} no es válido ({error}). Ejecuta de nuevo el rastreo.")
        if not recipes:
            raise SystemExit(f"{path} no contiene recetas.")
        print(f"{path}: {len(recipes)} recetas")


def index():
    subprocess.run([sys.executable, "indexer/indexer.py"], check=True)


def main():
    parser = argparse.ArgumentParser(description="Rastrea las fuentes e indexa las recetas.")
    parser.add_argument(
        "--sin-crawl",
        action="store_true",
        help="no rastrear: reindexar los JSON que ya existen en data/",
    )
    args = parser.parse_args()

    if not args.sin_crawl:
        crawl()

    check_data()
    index()


if __name__ == "__main__":
    main()
