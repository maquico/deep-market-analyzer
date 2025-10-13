# Tavily Search Lambda Service

Servicio AWS Lambda que proporciona las 4 funcionalidades principales de búsqueda web usando la API de Tavily: **Search**, **Extract**, **Crawl** y **Map**.

## 📋 Características

- **🔍 Search**: Búsqueda web completa con resultados detallados, respuestas IA, e imágenes
- **📄 Extract**: Extrae contenido limpio de URLs específicas (máx. 10 URLs)
- **🕷️ Crawl**: Crawlea sitios web recursivamente hasta 3 niveles de profundidad
- **🗺️ Map**: Mapea resultados de búsqueda con relaciones y contexto estructurado

## 🚀 Estructura del Proyecto

```
.
├── handler.py           # Código principal con 4 funciones de Tavily
├── serverless.yml       # Configuración de Serverless Framework
├── requirements.txt     # Dependencias de Python
├── .gitignore          # Archivos ignorados por Git
└── README.md           # Este archivo
```

## 📦 Requisitos Previos

1. **AWS CLI** configurado con credenciales
2. **Serverless Framework** instalado:
   ```bash
   npm install -g serverless
   ```
3. **Plugin de Python Requirements**:
   ```bash
   serverless plugin install -n serverless-python-requirements
   ```
4. **Python 3.11** instalado
5. **Cuenta de Tavily** y API Key (obtén una en [tavily.com](https://tavily.com))

## 🔧 Configuración

### 1. Clonar y configurar el proyecto

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
TAVILY_API_KEY=tu-api-key-aqui
```

O exporta la variable de entorno:

```bash
export TAVILY_API_KEY="tu-api-key-aqui"
```

## 🚢 Despliegue

### Desplegar a AWS

```bash
# Desplegar en staging (dev)
serverless deploy

# Desplegar en producción
serverless deploy --stage prod

# Desplegar en región específica
serverless deploy --region us-west-2
```

### Ver logs


```bash
serverless logs -f tavilySearch --tail
```

### Eliminar el servicio

```bash
serverless remove
```

## 📡 Uso de la API

### Endpoints Disponibles

Después del despliegue, obtendrás estos endpoints:

```
POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/tavily/search
POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/tavily/extract
POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/tavily/crawl
POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/tavily/map
```

**💡 Nota**: Cada endpoint mapea automáticamente a su función correspondiente. Solo envía los parámetros directamente en el body (sin necesidad de `action` o `parameters`).

---

## 1️⃣ SEARCH - Búsqueda Web Completa

Realiza búsquedas web con resultados detallados, respuestas generadas por IA e imágenes opcionales.

**Endpoint**: `POST /tavily/search`

### Request

```bash
curl -X POST https://tu-api-endpoint/dev/tavily/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Latest developments in quantum computing 2024",
    "max_results": 5,
    "search_depth": "advanced",
    "include_answer": true,
    "include_images": true,
    "include_raw_content": false,
    "topic": "general"
  }'
```

### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `query` | string | ✅ Sí | - | Consulta de búsqueda |
| `search_depth` | string | No | "basic" | "basic" o "advanced" |
| `max_results` | int | No | 5 | Máximo de resultados (1-20) |
| `include_answer` | bool | No | false | Incluir respuesta generada por IA |
| `include_images` | bool | No | false | Incluir imágenes relacionadas |
| `include_raw_content` | bool | No | false | Incluir HTML crudo |
| `include_domains` | array | No | null | Lista de dominios a incluir |
| `exclude_domains` | array | No | null | Lista de dominios a excluir |
| `topic` | string | No | "general" | "general" o "news" |

### Response

```json
{
  "action": "search",
  "result": {
    "success": true,
    "data": {
      "query": "Latest developments in quantum computing 2024",
      "answer": "Recent advancements in quantum computing include...",
      "results": [
        {
          "title": "Quantum Computing Breakthrough 2024",
          "url": "https://example.com/quantum-news",
          "content": "Scientists have achieved...",
          "score": 0.98,
          "published_date": "2024-10-01"
        }
      ],
      "images": [
        {
          "url": "https://example.com/image.jpg",
          "description": "Quantum processor"
        }
      ]
    }
  }
}
```

---

## 2️⃣ EXTRACT - Extraer Contenido de URLs

Extrae contenido limpio y parseado de hasta 10 URLs específicas.

### Request

```bash
curl -X POST https://tu-api-endpoint/dev/tavily/search \
  -H "Content-Type: application/json" \
  -d '{
    "action": "extract",
    "parameters": {
      "urls": [
        "https://example.com/article1",
        "https://example.com/article2",
        "https://blog.example.org/post123"
      ]
    }
  }'
```

### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `urls` | array | ✅ Sí | - | Lista de URLs (máx. 10) |

### Response

```json
{
  "action": "extract",
  "result": {
    "success": true,
    "data": {
      "results": [
        {
          "url": "https://example.com/article1",
          "raw_content": "Full article text...",
          "title": "Article Title",
          "author": "John Doe",
          "published_date": "2024-09-15"
        }
      ],
      "failed_results": [
        {
          "url": "https://example.com/article2",
          "error": "Page not found"
        }
      ]
    }
  }
}
```

---

## 3️⃣ CRAWL - Crawlear Sitios Web

Crawlea recursivamente un sitio web, extrayendo contenido de múltiples páginas.

### Request

```bash
curl -X POST https://tu-api-endpoint/dev/tavily/search \
  -H "Content-Type: application/json" \
  -d '{
    "action": "crawl",
    "parameters": {
      "url": "https://docs.example.com",
      "max_depth": 2,
      "max_pages": 20,
      "include_subdomains": false,
      "exclude_patterns": ["/admin/*", "/login"]
    }
  }'
```

### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `url` | string | ✅ Sí | - | URL inicial para crawlear |
| `max_depth` | int | No | 1 | Profundidad máxima (máx. 3) |
| `max_pages` | int | No | 10 | Máximo de páginas (máx. 100) |
| `include_subdomains` | bool | No | false | Incluir subdominios |
| `exclude_patterns` | array | No | null | Patrones de URL a excluir |

### Response

```json
{
  "action": "crawl",
  "result": {
    "success": true,
    "data": {
      "start_url": "https://docs.example.com",
      "total_pages": 15,
      "pages": [
        {
          "url": "https://docs.example.com/intro",
          "title": "Introduction",
          "content": "Welcome to our documentation...",
          "depth": 1,
          "links": ["https://docs.example.com/getting-started"]
        },
        {
          "url": "https://docs.example.com/getting-started",
          "title": "Getting Started",
          "content": "Follow these steps...",
          "depth": 2
        }
      ]
    }
  }
}
```

---

## 4️⃣ MAP - Mapear Resultados de Búsqueda

Mapea resultados de búsqueda mostrando relaciones, dominios y contexto estructurado.

### Request

```bash
curl -X POST https://tu-api-endpoint/dev/tavily/search \
  -H "Content-Type: application/json" \
  -d '{
    "action": "map",
    "parameters": {
      "query": "Best practices for microservices architecture",
      "search_depth": "advanced",
      "max_results": 10,
      "include_domains": ["medium.com", "dev.to"],
      "exclude_domains": ["spam-site.com"]
    }
  }'
```

### Parámetros

| Parámetro | Tipo | Requerido | Default | Descripción |
|-----------|------|-----------|---------|-------------|
| `query` | string | ✅ Sí | - | Consulta de búsqueda |
| `search_depth` | string | No | "advanced" | "basic" o "advanced" |
| `max_results` | int | No | 5 | Máximo de resultados |
| `include_domains` | array | No | null | Dominios a incluir |
| `exclude_domains` | array | No | null | Dominios a excluir |

### Response

```json
{
  "action": "map",
  "result": {
    "success": true,
    "data": {
      "query": "Best practices for microservices architecture",
      "answer": "Key best practices include...",
      "total_results": 10,
      "domains": [
        "medium.com",
        "dev.to",
        "martinfowler.com"
      ],
      "sources": [
        {
          "url": "https://medium.com/microservices-guide",
          "title": "Microservices Architecture Guide",
          "content": "This comprehensive guide covers...",
          "score": 0.95,
          "domain": "medium.com"
        }
      ]
    }
  }
}
```

---

## 🧪 Testing Local

Puedes probar las funciones localmente ejecutando:

```bash
python handler.py
```

Esto ejecutará los 4 casos de prueba incluidos en el archivo.

---

## 💡 Casos de Uso

### Search
- Búsquedas generales en la web
- Investigación con respuestas IA
- Búsquedas de noticias recientes
- Recopilación de información con imágenes

### Extract
- Extraer artículos de blogs
- Leer contenido de múltiples URLs
- Parsear documentación
- Obtener texto limpio de páginas web

### Crawl
- Indexar documentación completa
- Crear base de conocimientos de un sitio
- Análisis de contenido de sitios web
- Backup de contenido web

### Map
- Análisis de fuentes de información
- Visualización de dominios relacionados
- Contexto estructurado para RAG
- Mapeo de relaciones entre fuentes


## 👥 Autores

William Ferreira, Luis Adames, Angel Moreno

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

**Desarrollado para AWS Hackathon 2025** 🚀