# Buscador de Recetas Gallegas

Proyecto de la asignatura **Recuperación de Información y Web Semántica** (Máster Universitario en Ingeniería Informática, Universidade da Coruña).

Buscador web sobre recetas tradicionales de Galicia: crawling de dos fuentes, indexación con Elasticsearch e integración de un LLM para respuestas enriquecidas.

---

## Dominio

Recetas tradicionales gallegas, escritas en gallego. Hoy están repartidas entre blogs y sitios pequeños; el buscador permite encontrarlas en un solo lugar por nombre (tarta de Santiago) o por ingrediente (castañas).

**Fuentes de datos:**

| Fuente | Tipo | Semilla | Recetas |
|--------|------|---------|---------|
| [kukinhas.com](https://kukinhas.com) | Blog de una autora, textos largos | https://kukinhas.com/receitas-tradicionais/ 
| [receitario.gal](https://receitario.gal) | Wiki colaborativo, recetas breves | https://receitario.gal/category/receitas-tradicionais/ | 94 |

**Esquema común** (el mismo en las dos fuentes):

| Campo | Descripción |
|-------|-------------|
| `recipe_id` | Identificador estable: SHA-1 de la URL (16 caracteres) |
| `title` | Título de la receta |
| `ingredients` | Lista de ingredientes |
| `preparation` | Texto de la preparación |
| `url` | URL de la receta |
| `source` | Sitio de origen (`Kukinhas`, `Receitario`) |

---

## Arquitectura

```
Crawlers (Scrapy)
      │
      ▼
Indexación (Elasticsearch)
      │
      ▼
Backend (API de búsqueda + integración LLM)
      │
      ▼
Interfaz web
```

---

## Estructura del proyecto

```
recipes-search/
├── crawlers/          # Spiders de Scrapy para cada fuente
├── data/              # Datos crudos y procesados (excluidos del repo)
├── indexer/           # Scripts de mapping e indexación en Elasticsearch
├── search/            # Lógica de búsqueda y estrategia de ranking
├── llm/               # Integración con el servidor LLM (RAG)
├── web/               # Aplicación web
│   ├── backend/       # API con FastAPI (búsqueda y, más adelante, LLM)
│   └── frontend/      # Interfaz en HTML, CSS y JS
├── main.py            # Rastrea las fuentes e indexa las recetas
└── README.md
```

---

## Tecnologías

- **Python 3.x** — crawling, procesamiento e indexación
- **Scrapy** — rastreo y extracción de las fuentes
- **Elasticsearch** — índice y estrategia de búsqueda (BM25 + campos ponderados, analizador gallego)
- **LLM del servidor de la asignatura** — generación de respuestas RAG
- **FastAPI + Uvicorn** — backend de la aplicación web
- **HTML, CSS y JavaScript** — interfaz web (sin build), servida por el propio backend

---

## Instalación

Todos los comandos se ejecutan desde la **raíz del repositorio** (la carpeta `recipes-search`).

### Requisitos

- Python 3.10+
- Docker (para ejecutar Elasticsearch)
- Credenciales del servidor LLM de la asignatura en un archivo `.env` (no incluidas en el repo)

### Paso 1. Instalar (solo la primera vez)

```bash
git clone https://github.com/nathcarnevalli/recipes-search.git
cd recipes-search
sudo apt install python3-venv      # solo Ubuntu/Debian/WSL, si no lo tienes
python3 -m venv .venv
source .venv/bin/activate    
pip install -r requirements.txt
```

### Paso 2. Encender Elasticsearch

Elasticsearch debe estar encendido **antes** de indexar o de abrir la web.

Si ya existe:

```bash
docker start es
```

Si no existe (primera vez), se crea y arranca con:

```bash
docker run -d --name es -p 9200:9200 \
  -e "discovery.type=single-node" -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.19.3
```

### Paso 3. Cargar las recetas en el índice

Los datos ya vienen en `data/kukinhas.json` y `data/receitario.json`, así que normalmente **no hace falta rastrear**. Solo se indexa:

```bash
python main.py --sin-crawl
```

**Opcional: rastrear las fuentes** (tarda unos 7 minutos por el retardo entre peticiones de receitario):

```bash
python main.py
```

### Paso 4. Arrancar la aplicación web

```bash
uvicorn web.backend.main:app --reload
```

Abre http://localhost:8000.

### Uso diario (resumen)

```bash
cd recipes-search
docker start es
source .venv/bin/activate
uvicorn web.backend.main:app --reload
```
---

## Autores
- Nathalia
- Rafael
- Alex
