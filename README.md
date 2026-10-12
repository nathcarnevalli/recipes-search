# Buscador de Recetas Gallegas

Proyecto de la asignatura **Recuperación de Información y Web Semántica** (Máster Universitario en Ingeniería Informática, Universidade da Coruña).

Buscador web sobre recetas tradicionales de Galicia: crawling de dos fuentes, indexación con Elasticsearch e integración de un LLM para respuestas enriquecidas.

---

## Dominio

Las recetas gallegas se caracterizan por ingredientes frescos del mar y la tierra: mariscos, pescados, verduras, pan, aceite de oliva y hierbas aromáticas. El buscador permite encontrar recetas por nombre, ingrediente, técnica o tipo de plato.

**Fuentes de datos:**

| Fuente | URL | Tipo de contenido |
|--------|-----|------------------|
| Kukinhas | https://kukinhas.com | Blog de recetas gallegas con estructura por fecha |
| Receitario | https://receitario.gal | Repositorio de recetas tradicionales gallegas |

---

## Arquitectura

```
Crawlers (Scrapy)
      │
      ▼
Preparación de datos (limpieza, unificación de esquema)
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
├── web/               # Interfaz web
├── main.py
└── README.md
```

---

## Tecnologías

- **Python 3.x** — crawling, procesamiento e indexación
- **Scrapy** — rastreo y extracción de las fuentes
- **Elasticsearch** — índice y estrategia de búsqueda (BM25 + campos ponderados)
- **LLM del servidor de la asignatura** — generación de respuestas RAG
- **Framework web** — _por definir_ (Flask / FastAPI + frontend)

---

## Puesta en marcha

### Requisitos previos

- Python 3.10+
- Elasticsearch 8.x en ejecución local (`localhost:9200`)
- Credenciales del servidor LLM de la asignatura en `.env` (no incluidas en el repo)

### Instalación

```bash
pip install -r requirements.txt
```

### 1. Crawling

```bash
# Fuente 1
scrapy crawl <spider1> -o data/raw/source1.jsonl

# Fuente 2
scrapy crawl <spider2> -o data/raw/source2.jsonl
```

### 2. Preparación de datos

```bash
python indexer/prepare.py
```

Unifica las dos fuentes en un esquema común con los campos: `id`, `title`, `ingredients`, `instructions`, `url`, `source`.

### 3. Indexación

```bash
python indexer/index.py
```

Crea el índice con el mapping definido y carga los documentos en Elasticsearch.

### 4. Aplicación web

```bash
python main.py
```

La interfaz estará disponible en `http://localhost:5000`.

## Autores

- Nathalia Mesquita Carnevalli
- Rafael
- Alex
