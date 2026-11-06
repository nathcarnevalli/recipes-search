from pathlib import Path

from elasticsearch import ConnectionError as ESConnectionError
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from search.search import client, search_recipes

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
SNIPPET_LENGTH = 300

app = FastAPI(title="Buscador de recetas gallegas")


class Recipe(BaseModel):
    recipe_id: str | None = None
    title: str
    ingredients: list[str]
    snippet: str
    url: str
    source: str
    score: float


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[Recipe]


def to_recipe(hit):
    recipe = hit["_source"]
    ingredients = recipe.get("ingredients", [])
    if not isinstance(ingredients, list):
        ingredients = [ingredients]

    preparation = recipe.get("preparation", "")
    snippet = preparation[:SNIPPET_LENGTH]
    if len(preparation) > SNIPPET_LENGTH:
        snippet += "..."

    return Recipe(
        recipe_id=recipe.get("recipe_id"),
        title=recipe.get("title", "Sin título"),
        ingredients=ingredients,
        snippet=snippet,
        url=recipe.get("url", ""),
        source=recipe.get("source", "Desconocida"),
        score=hit["_score"] or 0.0,
    )


@app.get("/api/health")
def health():
    return {"elasticsearch": client.ping()}


@app.get("/api/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, description="Texto de búsqueda"),
    size: int = Query(10, ge=1, le=50),
    source: str | None = Query(None, description="Filtra por fuente"),
):
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="La búsqueda no puede estar vacía.")

    try:
        hits = search_recipes(query, size=size, source=source)
    except ESConnectionError:
        raise HTTPException(status_code=503, detail="No se pudo conectar con Elasticsearch.")

    results = [to_recipe(hit) for hit in hits]
    return SearchResponse(query=query, total=len(results), results=results)


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
