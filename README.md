# Buscador de Recetas Gallegas

Proyecto de la asignatura **Recuperación de Información y Web Semántica** (Máster Universitario en Ingeniería Informática, Universidade da Coruña).

Buscador web sobre recetas tradicionales de Galicia: crawling de dos fuentes, indexación con Elasticsearch e integración de un LLM para respuestas enriquecidas.

---

## Dominio

Recetas tradicionales gallegas, escritas en gallego. Hoy están repartidas entre blogs y sitios pequeños; el buscador permite encontrarlas en un solo lugar por nombre (tarta de Santiago) o por ingrediente (castañas).

**Fuentes de datos:**

| Fuente | Tipo | Semilla | Recetas |
|--------|------|---------|---------|
| [kukinhas.com](https://kukinhas.com) | Blog de una autora, textos largos | https://kukinhas.com/receitas-tradicionais/ | ~46 |
| [receitario.gal](https://receitario.gal) | Wiki colaborativo, recetas breves | https://receitario.gal/category/receitas-tradicionais/ | 95 |

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
- **Elasticsearch** — índice y estrategia de búsqueda (BM25 + campos ponderados, analizador gallego)
- **LLM del servidor de la asignatura** — generación de respuestas RAG
- **Framework web** — _por definir_

---

## Puesta en marcha

### Requisitos previos

- Python 3.10+
- Elasticsearch 8.x en ejecución local
- Credenciales del servidor LLM de la asignatura en `.env` (no incluidas en el repo)

### Instalación

Todos los comandos se ejecutan desde la **raíz del repositorio**.

```bash
# 1. Clonar el repositorio
git clone https://github.com/nathcarnevalli/recipes-search.git
cd recipes-search

# 2. Crear el entorno virtual
python3 -m venv .venv

# 3. Activarlo
source .venv/bin/activate        # Linux / macOS / WSL
# .venv\Scripts\activate         # Windows

# 4. Instalar las dependencias
pip install -r requirements.txt

# 5. Ejecutar crawlers
scrapy runspider crawlers/exploracion/muestra_kukinhas.py -O data/muestras/muestra_kukinhas.json
scrapy runspider crawlers/exploracion/muestra_receitario.py -O data/muestras/muestra_receitario.json
```

---

## Autores

- Nathalia
- Rafael
- Alex
