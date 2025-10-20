# Tavily Search Lambda Service

AWS Lambda service that provides the 4 main web search functionalities using the Tavily API: **Search**, **Extract**, **Crawl**, and **Map**.

## 📋 Features

- **🔍 Search**: Complete web search with detailed results, AI-generated answers, and images
- **📄 Extract**: Extracts clean content from specific URLs (max. 10 URLs)
- **🕷️ Crawl**: Crawls websites recursively up to 3 levels deep
- **🗺️ Map**: Maps search results with relationships and structured context

## 🚀 Project Structure

```
.
├── handler.py           # Main code with 4 Tavily functions
├── serverless.yml       # Serverless Framework configuration
├── requirements.txt     # Python dependencies
├── .gitignore          # Files ignored by Git
└── README.md           # This file
```

## 📦 Prerequisites

1. **AWS CLI** configured with credentials
2. **Serverless Framework** installed:
   ```bash
   npm install -g serverless
   ```
3. **Python Requirements Plugin**:
   ```bash
   serverless plugin install -n serverless-python-requirements
   ```
4. **Python 3.11** installed
5. **Tavily Account** and API Key (get one at [tavily.com](https://tavily.com))

## 🔧 Configuration

### 1. Clone and setup the project

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
TAVILY_API_KEY=your-api-key-here
```

Or export the environment variable:

```bash
export TAVILY_API_KEY="your-api-key-here"
```

## 🚢 Deployment

### Deploy to AWS

```bash
# Deploy to staging (dev)
serverless deploy

# Deploy to production
serverless deploy --stage prod

# Deploy to specific region
serverless deploy --region us-west-2
```

### View logs


```bash
serverless logs -f tavilySearch --tail
```

### Remove the service

```bash
serverless remove
```

## 📡 API Usage

### Available Endpoints

After deployment, you'll get these endpoints:

```
POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/tavily/search
POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/tavily/extract
POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/tavily/crawl
POST https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/dev/tavily/map
```

**💡 Note**: Each endpoint automatically maps to its corresponding function. Just send parameters directly in the body (no need for `action` or `parameters`).

---

## 1️⃣ SEARCH - Complete Web Search

Performs web searches with detailed results, AI-generated answers, and optional images.

**Endpoint**: `POST /tavily/search`

### Request

```bash
curl -X POST https://your-api-endpoint/dev/tavily/search \
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

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Search query |
| `search_depth` | string | No | "basic" | "basic" or "advanced" |
| `max_results` | int | No | 5 | Maximum results (1-20) |
| `include_answer` | bool | No | false | Include AI-generated answer |
| `include_images` | bool | No | false | Include related images |
| `include_raw_content` | bool | No | false | Include raw HTML |
| `include_domains` | array | No | null | List of domains to include |
| `exclude_domains` | array | No | null | List of domains to exclude |
| `topic` | string | No | "general" | "general" or "news" |

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

## 2️⃣ EXTRACT - Extract Content from URLs

Extracts clean and parsed content from up to 10 specific URLs.

### Request

```bash
curl -X POST https://your-api-endpoint/dev/tavily/search \
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

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `urls` | array | ✅ Yes | - | List of URLs (max. 10) |

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

## 3️⃣ CRAWL - Crawl Websites

Recursively crawls a website, extracting content from multiple pages.

### Request

```bash
curl -X POST https://your-api-endpoint/dev/tavily/search \
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

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ Yes | - | Starting URL to crawl |
| `max_depth` | int | No | 1 | Maximum depth (max. 3) |
| `max_pages` | int | No | 10 | Maximum pages (max. 100) |
| `include_subdomains` | bool | No | false | Include subdomains |
| `exclude_patterns` | array | No | null | URL patterns to exclude |

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

## 4️⃣ MAP - Map Search Results

Maps search results showing relationships, domains, and structured context.

### Request

```bash
curl -X POST https://your-api-endpoint/dev/tavily/search \
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

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | Search query |
| `search_depth` | string | No | "advanced" | "basic" or "advanced" |
| `max_results` | int | No | 5 | Maximum results |
| `include_domains` | array | No | null | Domains to include |
| `exclude_domains` | array | No | null | Domains to exclude |

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

## 🧪 Local Testing

You can test the functions locally by running:

```bash
python handler.py
```

This will execute the 4 test cases included in the file.

---

## 💡 Use Cases

### Search
- General web searches
- Research with AI answers
- Recent news searches
- Information gathering with images

### Extract
- Extract blog articles
- Read content from multiple URLs
- Parse documentation
- Get clean text from web pages

### Crawl
- Index complete documentation
- Create knowledge base from a site
- Website content analysis
- Web content backup

### Map
- Information source analysis
- Related domain visualization
- Structured context for RAG
- Source relationship mapping


## 👥 Authors

Angel Moreno, Luis Adames, William Ferreira

## 📄 License

This project is under the MIT license.

---

**Developed for AWS Hackathon 2025** 🚀