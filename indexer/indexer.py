import json
from elasticsearch import Elasticsearch

client = Elasticsearch("http://localhost:9200")
index_name = "receitas_galegas"

# Leer las recetas de los archivos JSON: una lista de recetas por fuente
recipes = []

for path in ["data/kukinhas.json", "data/receitario.json"]:
    with open(path, encoding="utf-8") as f:
        recipes.extend(json.load(f))

if not recipes:
    raise SystemExit("Los archivos JSON no contienen recetas.")

# Comprobar que las recetas tienen los campos necesarios
required_fields = [
    "recipe_id",
    "title",
    "ingredients",
    "preparation",
    "url",
    "source",
]

for i, recipe in enumerate(recipes, start=1):
    missing = [field for field in required_fields if field not in recipe]
    if missing:
        raise SystemExit(
            f"Receta {i} incompleta. Faltan los campos: {missing}"
        )

# Crear el índice desde cero para esta prueba
if client.indices.exists(index=index_name):
    client.indices.delete(index=index_name)

client.indices.create(
    index=index_name,
    mappings={
        "properties": {
            "recipe_id": {"type": "keyword"},
            "title": {"type": "text"},
            "ingredients": {"type": "text"},
            "preparation": {"type": "text"},
            "url": {"type": "keyword"},
            "source": {"type": "keyword"},
        }
    },
)

# Indexar las recetas
for recipe in recipes:
    client.index(
        index=index_name,
        id=recipe["recipe_id"],
        document=recipe,
    )

client.indices.refresh(index=index_name)

print("Recetas leídas:", len(recipes))
print("Documentos indexados:", client.count(index=index_name)["count"])
