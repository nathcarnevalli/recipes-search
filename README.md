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
- **Web** — _por definir_

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
 
# 2. Crear el entorno virtual (aísla las dependencias del proyecto)
python3 -m venv .venv
 
# 3. Activarlo (hay que repetirlo en cada terminal nueva)
source .venv/bin/activate        # Linux / macOS / WSL
# .venv\Scripts\activate         # Windows
 
# 4. Instalar las dependencias
pip install -r requirements.txt
 
# 5. Comprobar que Scrapy está disponible
scrapy version
```
 
Si se añade una dependencia nueva, hay que actualizar el archivo con `pip freeze > requirements.txt`.

## Autores

- Nathalia Mesquita Carnevalli
- Rafael
- Alex
