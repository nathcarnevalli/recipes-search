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

**Receitario.** El spider ([crawlers/receitario_spider.py](crawlers/receitario_spider.py)) recorre el listado de la categoría, sigue la paginación y entra en cada receta. Cada receta separa sus secciones con un `<h2>`: el spider reparte las líneas en `ingredients` o `preparation` según el encabezado ("Ingredientes", "Preparación") e ignora el resto (historia, notas). No guarda las páginas que no tienen ingredientes o preparación, como el caldo de cocido. Con un `DOWNLOAD_DELAY` de 2 s el sitio devolvía errores 429, por lo que se usa 4 s.

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

# 5. Rastrear las dos fuentes e indexar las recetas en Elasticsearch
python main.py
```

`main.py` rastrea las dos fuentes a la vez (generan `data/kukinhas.json` y `data/receitario.json`), comprueba que los archivos son válidos y lanza el indexador. El rastreo de receitario tarda unos 7 minutos por el retardo entre peticiones. Elasticsearch debe estar en ejecución antes de empezar.

Para reindexar sin volver a rastrear, usando los JSON que ya existen en `data/`:

```bash
python main.py --sin-crawl
```

Cada paso también se puede ejecutar por separado:

```bash
scrapy runspider crawlers/kukinhas_spider.py
scrapy runspider crawlers/receitario_spider.py
python indexer/indexer.py
```

No se deben ejecutar dos rastreos de la misma fuente a la vez: escriben en el mismo archivo y lo corrompen.

Los spiders de exploración (muestras pequeñas para validar las fuentes) siguen disponibles:

```bash
scrapy runspider crawlers/muestras/muestra_kukinhas.py -O data/muestras/muestra_kukinhas.json
scrapy runspider crawlers/muestras/muestra_receitario.py -O data/muestras/muestra_receitario.json
```

### Aplicación web

Con Elasticsearch en ejecución y el índice ya creado, desde la raíz del repositorio:

```bash
uvicorn web.backend.main:app --reload
```

Después se abre http://localhost:8000. La documentación interactiva de la API está en http://localhost:8000/docs.

Endpoints principales:

- `GET /api/search?q=<texto>&size=10&source=<fuente>` — busca recetas. `size` (1-50) y `source` (`Kukinhas` o `Receitario`) son opcionales.
- `GET /api/health` — indica si Elasticsearch responde.

Si aparece _No se pudo conectar con Elasticsearch_, Elasticsearch no está en ejecución. Con Docker: `docker start es` (o el nombre del contenedor que se haya creado).

Si aparece `[Errno 98] Address already in use`, hay otro servidor ocupando el puerto 8000: se cierra con `Ctrl+C` (no `Ctrl+Z`, que solo lo suspende y deja el puerto ocupado) o se usa otro puerto con `--port 8001`.

### Guía rápida de ejecución

Todos los comandos se ejecutan desde la raíz del repositorio.

**1. Primera vez (preparación)**

```bash
cd recipes-search
python3 -m venv .venv              # solo si la .venv no existe
source .venv/bin/activate
pip install -r requirements.txt
```

**2. Encender Elasticsearch**

```bash
docker start es
curl localhost:9200                # debe responder con un JSON
```

**3. Crear el índice** (solo si todavía no existe o si los datos cambian)

```bash
python indexer/indexer.py          # indexa los data/*.json
```

O, para volver a rastrear las fuentes e indexar (tarda unos 7 minutos):

```bash
python main.py
```

**4. Arrancar la aplicación web**

```bash
uvicorn web.backend.main:app --reload
```

Se abre http://localhost:8000. Swagger está en http://localhost:8000/docs.

**5. Parar**

- Servidor: `Ctrl+C` (no `Ctrl+Z`).
- Elasticsearch: `docker stop es`.

**Uso diario (resumen)**

```bash
cd recipes-search
docker start es
source .venv/bin/activate
uvicorn web.backend.main:app --reload
```

**Búsqueda por terminal, sin la web (opcional)**

```bash
python search/search.py
```

---

## Autores
- Nathalia
- Rafael
- Alex
