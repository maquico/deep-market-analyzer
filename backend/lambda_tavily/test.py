import requests
import json
from typing import Dict, List, Optional, Any


class TavilySearchClient:
    """Client to interact with Tavily Search Lambda"""
    
    def __init__(self, base_url: str = "https://knfgymajqd.execute-api.us-east-1.amazonaws.com/dev"):
        """
        Initialize client
        
        Args:
            base_url: Base URL of the API Gateway
        """
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 5,
        include_images: bool = False,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        topic: str = "general"
    ) -> Dict[str, Any]:
        """
        Perform web search
        
        Args:
            query: Search query
            search_depth: 'basic' or 'advanced'
            max_results: Maximum results (1-20)
            include_images: Include images
            include_answer: Include AI answer
            include_raw_content: Include raw HTML
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            topic: 'general' or 'news'
        
        Returns:
            Dict with search results
        """
        url = f"{self.base_url}/tavily/search"
        
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
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def extract(self, urls: List[str]) -> Dict[str, Any]:
        """
        Extract content from URLs
        
        Args:
            urls: List of URLs (maximum 10)
        
        Returns:
            Dict with extracted content
        """
        if len(urls) > 10:
            raise ValueError("Maximum 10 URLs allowed")
        
        url = f"{self.base_url}/tavily/extract"
        payload = {"urls": urls}
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def crawl(
        self,
        url: str,
        max_depth: int = 1,
        max_pages: int = 10,
        include_subdomains: bool = False,
        exclude_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Crawl website
        
        Args:
            url: Starting URL
            max_depth: Maximum depth (1-3)
            max_pages: Maximum pages (1-100)
            include_subdomains: Include subdomains
            exclude_patterns: Patterns to exclude
        
        Returns:
            Dict with crawled pages
        """
        endpoint = f"{self.base_url}/tavily/crawl"
        
        payload = {
            "url": url,
            "max_depth": max_depth,
            "max_pages": max_pages,
            "include_subdomains": include_subdomains
        }
        
        if exclude_patterns:
            payload["exclude_patterns"] = exclude_patterns
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def map_results(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Map search results
        
        Args:
            query: Search query
            search_depth: 'basic' or 'advanced'
            max_results: Maximum results
            include_domains: Domains to include
            exclude_domains: Domains to exclude
        
        Returns:
            Dict with mapped results
        """
        url = f"{self.base_url}/tavily/map"
        
        payload = {
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results
        }
        
        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()


# ============================================
# USAGE EXAMPLES
# ============================================

if __name__ == "__main__":
    # Initialize client
    client = TavilySearchClient()
    
    # Example 1: Simple search
    print("=== EXAMPLE 1: Simple search ===")
    result = client.search(
        query="Python tutorials 2024",
        max_results=3
    )
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Example 2: Advanced search with AI answer
    print("=== EXAMPLE 2: Search with AI ===")
    result = client.search(
        query="Best practices for microservices",
        search_depth="advanced",
        max_results=5,
        include_answer=True,
        include_images=True
    )
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Example 3: Search with domain filters
    print("=== EXAMPLE 3: Filtered search ===")
    result = client.search(
        query="AI news",
        include_domains=["techcrunch.com", "venturebeat.com"],
        max_results=5
    )
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Example 4: Extract content
    print("=== EXAMPLE 4: Extract content ===")
    result = client.extract(
        urls=[
            "https://www.python.org/about/"
        ]
    )
    print(json.dumps(result, indent=2))
    print("\n")
    
    #Example 5: Crawl website
    print("=== EXAMPLE 5: Crawl website ===")
    result = client.crawl(
        url="https://docs.python.org/3/tutorial/",
        max_depth=2,
        max_pages=5
    )
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Example 6: Map results
    print("=== EXAMPLE 6: Map results ===")
    result = client.map_results(
        query="Climate change solutions",
        max_results=10,
        search_depth="advanced"
    )
    print(json.dumps(result, indent=2))
    print("\n")
    
    # Example 7: Error handling
    print("=== EXAMPLE 7: Error handling ===")
    # try:
    #     result = client.extract(urls=[])  # Empty URLs, will cause error
    # except requests.exceptions.HTTPError as e:
    #     print(f"HTTP Error: {e}")
    #     print(f"Response: {e.response.text}")