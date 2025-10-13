import json
import os
import requests
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_API_URL = "https://api.tavily.com"


def search(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 5,
    include_images: bool = False,
    include_answer: bool = False,
    include_raw_content: bool = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    topic: str = "general"
) -> Dict[str, Any]:
    """
    Perform a web search using Tavily API.
    
    Args:
        query: The search query
        search_depth: "basic" or "advanced" (default: "basic")
        max_results: Maximum number of results (1-20, default: 5)
        include_images: Whether to include images in results
        include_answer: Whether to include AI-generated answer
        include_raw_content: Whether to include raw HTML content
        include_domains: List of domains to include in search
        exclude_domains: List of domains to exclude from search
        topic: Search topic - "general" or "news" (default: "general")
    
    Returns:
        Dict containing search results
    """
    try:
        url = f"{TAVILY_API_URL}/search"
        
        payload = {
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_images": include_images,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "topic": topic
        }
        
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        
        headers = {
            "Authorization": f"Bearer {TAVILY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        return {
            "success": True,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def extract(urls: List[str]) -> Dict[str, Any]:
    """
    Extract clean content from specific URLs.
    
    Args:
        urls: List of URLs to extract content from (max 10 URLs)
    
    Returns:
        Dict containing extracted content
    """
    try:
        print(f"Starting extract with urls: {urls}")
        
        if not urls or len(urls) == 0:
            raise ValueError("urls parameter is required and must contain at least one URL")
        
        if len(urls) > 10:
            raise ValueError("Maximum 10 URLs allowed per request")
        
        url = f"{TAVILY_API_URL}/extract"
        
        payload = {
            "urls": urls
        }
        
        headers = {
            "Authorization": f"Bearer {TAVILY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        print(f"Making request to {url} with payload: {payload}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        response.raise_for_status()
        
        data = response.json()
        
        print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
        
        return {
            "success": True,
            "data": {
                "results": data.get("results", []),
                "failed_results": data.get("failed_results", [])
            }
        }
    except requests.exceptions.RequestException as e:
        print(f"RequestException in extract: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    except Exception as e:
        print(f"Exception in extract: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def crawl(
    url: str,
    include_subdomains: bool = False,
    max_depth: int = 1,
    max_pages: int = 10,
    exclude_patterns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Crawl a website starting from a URL.
    
    Args:
        url: The starting URL to crawl
        include_subdomains: Whether to include subdomains in crawl (default: False)
        max_depth: Maximum depth to crawl (default: 1, max: 3)
        max_pages: Maximum number of pages to crawl (default: 10, max: 100)
        exclude_patterns: URL patterns to exclude from crawling
    
    Returns:
        Dict containing crawled pages
    """
    try:
        print(f"Starting crawl with params: url={url}, max_depth={max_depth}, max_pages={max_pages}")
        
        if not url:
            raise ValueError("url parameter is required")
        
        if max_depth > 3:
            raise ValueError("max_depth cannot exceed 3")
        
        if max_pages > 100:
            raise ValueError("max_pages cannot exceed 100")
        
        endpoint = f"{TAVILY_API_URL}/crawl"
        
        payload = {
            "url": url,
            "max_depth": max_depth,
            "max_pages": max_pages
        }
        
        if include_subdomains:
            payload["include_subdomains"] = include_subdomains
        
        if exclude_patterns:
            payload["exclude_patterns"] = exclude_patterns
        
        headers = {
            "Authorization": f"Bearer {TAVILY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        print(f"Making request to {endpoint} with payload: {payload}")
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        response.raise_for_status()
        
        data = response.json()
        print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not dict'}")
        
        return {
            "success": True,
            "data": {
                "pages": data.get("pages", []),
                "total_pages": len(data.get("pages", [])),
                "start_url": url
            }
        }
    except requests.exceptions.RequestException as e:
        print(f"RequestException in crawl: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    except Exception as e:
        print(f"Exception in crawl: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def search_map(
    query: str,
    search_depth: str = "advanced",
    max_results: int = 5,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Map search results to show relationships and connections.
    
    Args:
        query: The search query
        search_depth: "basic" or "advanced" (default: "advanced")
        max_results: Maximum number of results (default: 5)
        include_domains: List of domains to include
        exclude_domains: List of domains to exclude
    
    Returns:
        Dict containing mapped search results
    """
    try:
        # Usar la búsqueda normal y procesar los resultados para mapearlos
        search_result = search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_answer=True,
            include_raw_content=False
        )
        
        if not search_result.get("success"):
            return search_result
        
        response_data = search_result["data"]
        
        # Create a map structure with enhanced metadata
        mapped_results = {
            "query": query,
            "answer": response_data.get("answer", ""),
            "sources": [],
            "domains": set(),
            "total_results": len(response_data.get("results", []))
        }
        
        for result in response_data.get("results", []):
            source_info = {
                "url": result.get("url"),
                "title": result.get("title"),
                "content": result.get("content"),
                "score": result.get("score", 0),
                "domain": result.get("url", "").split("/")[2] if result.get("url") else None
            }
            mapped_results["sources"].append(source_info)
            if source_info["domain"]:
                mapped_results["domains"].add(source_info["domain"])
        
        # Convert set to list for JSON serialization
        mapped_results["domains"] = list(mapped_results["domains"])
        
        return {
            "success": True,
            "data": mapped_results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def lambda_handler(event, context):
    """
    AWS Lambda handler function for Tavily operations.
    
    Soporta dos métodos de invocación:
    
    1. Por ruta HTTP (recomendado):
       - POST /tavily/search con body: {"query": "...", "max_results": 5, ...}
       - POST /tavily/extract con body: {"urls": ["...", "..."]}
       - POST /tavily/crawl con body: {"url": "...", "max_depth": 2, ...}
       - POST /tavily/map con body: {"query": "...", "max_results": 5, ...}
    
    2. Por parámetro action (alternativo):
       - POST /tavily/search con body: {"action": "search", "parameters": {...}}
    
    Actions:
    - search: Full web search with detailed results
    - extract: Extract clean content from specific URLs
    - crawl: Recursively crawl a website
    - map: Map search results with relationships and context
    """
    try:
        print("Received event:", json.dumps(event))
        
        # Parse body if from API Gateway
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Determinar action desde la ruta o desde el body
        action = None
        parameters = {}
        
        # Método 1: Detectar action desde la ruta HTTP
        if 'path' in event:
            path = event['path']
            if '/search' in path:
                action = 'search'
                parameters = body  # Todo el body son parámetros
            elif '/extract' in path:
                action = 'extract'
                parameters = body
            elif '/crawl' in path:
                action = 'crawl'
                parameters = body
            elif '/map' in path:
                action = 'map'
                parameters = body
        
        # Método 2: Detectar action desde el body (retrocompatibilidad)
        if not action and 'action' in body:
            action = body.get('action')
            parameters = body.get('parameters', {})
        
        print(f"Action: {action}, Parameters: {parameters}")
        
        # Validate action
        if not action:
            raise ValueError("Could not determine action from path or body. Use /tavily/search, /tavily/extract, /tavily/crawl, or /tavily/map")
        
        # Route to appropriate function
        if action == "search":
            print(f"Executing search with parameters: {parameters}")
            result = search(**parameters)
        elif action == "extract":
            print(f"Executing extract with parameters: {parameters}")
            result = extract(**parameters)
        elif action == "crawl":
            print(f"Executing crawl with parameters: {parameters}")
            result = crawl(**parameters)
        elif action == "map":
            print(f"Executing map with parameters: {parameters}")
            result = search_map(**parameters)
        else:
            raise ValueError(f"Invalid action: {action}. Must be one of: search, extract, crawl, map")
        
        print(f"Function {action} completed with result success: {result.get('success', 'unknown')}")
        
        # Prepare response
        response_body = {
            "action": action,
            "result": result
        }
        
        # Return based on invocation type
        if 'body' in event:
            return {
                "statusCode": 200 if result.get("success") else 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps(response_body)
            }
        else:
            return response_body
            
    except Exception as e:
        error_response = {
            "error": str(e),
            "error_type": type(e).__name__
        }
        
        print(f"Error: {error_response}")
        
        if 'body' in event:
            return {
                "statusCode": 400 if isinstance(e, ValueError) else 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(error_response)
            }
        else:
            return error_response


# # Test examples
# if __name__ == "__main__":
#     # Test 1: Search
#     print("\n=== Test 1: Search ===")
#     test_event = {
#         "action": "search",
#         "parameters": {
#             "query": "Latest AI developments 2024",
#             "max_results": 3,
#             "include_answer": True,
#             "search_depth": "basic"
#         }
#     }
#     result = lambda_handler(test_event, None)
#     print(json.dumps(result, indent=2))
    
#     # Test 2: Extract
#     print("\n=== Test 2: Extract ===")
#     test_event = {
#         "action": "extract",
#         "parameters": {
#             "urls": ["https://example.com"]
#         }
#     }
#     result = lambda_handler(test_event, None)
#     print(json.dumps(result, indent=2))
    
#     # Test 3: Map
#     print("\n=== Test 3: Map ===")
#     test_event = {
#         "action": "map",
#         "parameters": {
#             "query": "Machine learning applications",
#             "max_results": 5
#         }
#     }
#     result = lambda_handler(test_event, None)
#     print(json.dumps(result, indent=2))