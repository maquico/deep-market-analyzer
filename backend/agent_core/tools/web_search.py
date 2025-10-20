import json
import requests
import os
from typing import Any, Dict, Optional

# ---- API Gateway endpoints ----
API_SEARCH = "https://knfgymajqd.execute-api.us-east-1.amazonaws.com/dev/tavily/search"
API_EXTRACT = "https://knfgymajqd.execute-api.us-east-1.amazonaws.com/dev/tavily/extract"
API_CRAWL = "https://knfgymajqd.execute-api.us-east-1.amazonaws.com/dev/tavily/crawl"
API_MAP = "https://knfgymajqd.execute-api.us-east-1.amazonaws.com/dev/tavily/map"

DEFAULT_TIMEOUT = int(os.environ.get("TAVILY_TIMEOUT", "90"))  # segundos

# ---- Helpers ----
def _parse_gateway_response(resp: requests.Response) -> Any:
    """
    Manages parsing API Gateway style responses vs direct JSON.
    """
    # Try parse JSON
    try:
        parsed = resp.json()
    except ValueError:
        # No JSON, devolver texto
        return {"ok": False, "response_text": resp.text, "status_code": resp.status_code}

    # If it's the API Gateway form with 'body'
    if isinstance(parsed, dict) and "body" in parsed:
        body = parsed["body"]
        # body can be dict or a JSON string: try to parse
        if isinstance(body, str):
            try:
                body_parsed = json.loads(body)
                return body_parsed
            except ValueError:
                # No JSON in body, return as-is with meta
                return {"ok": True, "body": body, "meta": {k: parsed.get(k) for k in ("statusCode", "headers")}}
        else:
            return body
    return parsed


def _post_json(url: str, payload: Dict, timeout: int = DEFAULT_TIMEOUT) -> Any:
    """
    Post simple with JSON payload and return parsed response.
    """
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
    except requests.RequestException as e:
        return {"ok": False, "error": "request_exception", "message": str(e)}

    # Try parse JSON
    parsed = _parse_gateway_response(resp)

    # If parse returns a dict with expected error keys
    return parsed


def tavily_search(query: str,
                  search_depth: str = "basic",
                  max_results: int = 5,
                  include_images: bool = False,
                  include_answer: bool = False,
                  include_raw_content: bool = False,
                  include_domains: Optional[list] = None,
                  exclude_domains: Optional[list] = None,
                  topic: str = "general",
                  api_url: str = API_SEARCH) -> Any:
    """
    Calls the /tavily/search (POST) endpoint.
    Minimum parameters: query.
    """
    if not query:
        return {"ok": False, "error": "missing_query"}

    # Normalize and validate parameters
    if search_depth not in ("basic", "advanced"):
        search_depth = "basic"
    if max_results < 1:
        max_results = 1
    if max_results > 20:
        max_results = 20

    payload = {
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results,
        "include_images": include_images,
        "include_answer": include_answer,
        "include_raw_content": include_raw_content,
        "include_domains": include_domains or [],
        "exclude_domains": exclude_domains or [],
        "topic": topic
    }
    return _post_json(api_url, payload)


def tavily_extract(urls: list,
                   api_url: str = API_EXTRACT) -> Any:
    """
    Calls the /tavily/extract endpoint with up to 10 URLs.
    """
    if not isinstance(urls, list) or len(urls) == 0:
        return {"ok": False, "error": "missing_urls"}
    if len(urls) > 10:
        return {"ok": False, "error": "too_many_urls", "max_allowed": 10}

    payload = {"urls": urls}
    return _post_json(api_url, payload)


def tavily_crawl(url: str,
                 max_depth: int = 1,
                 max_pages: int = 10,
                 include_subdomains: bool = False,
                 exclude_patterns: Optional[list] = None,
                 api_url: str = API_CRAWL) -> Any:
    """
    Calls the /tavily/crawl endpoint.
    max_depth: 1..3
    max_pages: 1..100
    """
    if not url:
        return {"ok": False, "error": "missing_url"}

    if max_depth < 1:
        max_depth = 1
    if max_depth > 3:
        max_depth = 3

    if max_pages < 1:
        max_pages = 1
    if max_pages > 100:
        max_pages = 100

    payload = {
        "url": url,
        "max_depth": max_depth,
        "max_pages": max_pages,
        "include_subdomains": bool(include_subdomains),
        "exclude_patterns": exclude_patterns or []
    }
    return _post_json(api_url, payload)


def tavily_map(query: str,
               search_depth: str = "advanced",
               max_results: int = 5,
               include_domains: Optional[list] = None,
               exclude_domains: Optional[list] = None,
               api_url: str = API_MAP) -> Any:
    """
    Calls the /tavily/map endpoint to get a concept map for the query.
    """
    if not query:
        return {"ok": False, "error": "missing_query"}

    if search_depth not in ("basic", "advanced"):
        search_depth = "advanced"

    payload = {
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results,
        "include_domains": include_domains or [],
        "exclude_domains": exclude_domains or []
    }
    return _post_json(api_url, payload)


if __name__ == "__main__":
    # Search
    res = tavily_search("python web scraping libraries", include_answer=True, max_results=3)
    print("Search result (sample):")
    try:
        print(json.dumps(res, indent=2, ensure_ascii=False)[:2000])
    except Exception:
        print(res)

    # Extract
    res2 = tavily_extract(["https://www.python.org/", "https://realpython.com/"])
    print("\nExtract result (sample):")
    try:
        print(json.dumps(res2, indent=2, ensure_ascii=False))
    except Exception:
        print(res2)
#
    ## Crawl
    res3 = tavily_crawl("https://gamerant.com/", max_depth=1, max_pages=5)
    print("\nCrawl result (sample):")
    try:
        print(json.dumps(res3, indent=2, ensure_ascii=False))
    except Exception:
        print(res3)
#
    ## Map
    res4 = tavily_map("serverless architectures", max_results=4)
    print("\nMap result (sample):")
    try:
        print(json.dumps(res4, indent=2, ensure_ascii=False))
    except Exception:
        print(res4)

