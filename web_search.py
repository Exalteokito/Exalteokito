import os
import requests
import serpapi
from bs4 import BeautifulSoup
from haystack import Document
import json
import time
from typing import List, Dict, Optional

class WebSearchQA:
    def __init__(self, serpapi_key: Optional[str] = None):
        self.serpapi_key = serpapi_key or os.getenv('SERPAPI_KEY')
        if not self.serpapi_key:
            print("Warning: No SerpAPI key provided. Web search will be disabled.")
            self.serpapi_key = None

    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search the web using SerpAPI and return relevant results."""
        if not self.serpapi_key:
            return []

        try:
            # Add sports-specific keywords to improve results
            sports_query = f"{query} sports news NBA basketball"

            params = {
                "engine": "google",
                "q": sports_query,
                "api_key": self.serpapi_key,
                "num": num_results,
                "tbm": "nws"  # News search for more current results
            }

            search = serpapi.GoogleSearch(params)
            results = search.get_dict()

            organic_results = results.get("organic_results", [])
            news_results = results.get("news_results", [])

            # Combine and deduplicate results
            all_results = news_results + organic_results
            seen_urls = set()
            unique_results = []

            for result in all_results:
                url = result.get('link')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
                    if len(unique_results) >= num_results:
                        break

            return unique_results[:num_results]

        except Exception as e:
            print(f"Web search error: {e}")
            return []

    def extract_content_from_url(self, url: str) -> str:
        """Extract and clean content from a URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Try to find main content (common selectors for sports sites)
            content_selectors = [
                'article',
                '.article-content',
                '.entry-content',
                '.post-content',
                '.content',
                '.story-body',
                'main',
                '[data-testid="article-body"]'
            ]

            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0].get_text(separator=' ', strip=True)
                    if len(content) > 200:  # Ensure we have substantial content
                        break

            # Fallback to body text if no specific content found
            if not content or len(content) < 200:
                content = soup.get_text(separator=' ', strip=True)

            # Clean up the content
            content = ' '.join(content.split())  # Normalize whitespace

            # Limit content length for processing
            if len(content) > 2000:
                content = content[:2000] + "..."

            return content

        except Exception as e:
            print(f"Content extraction error for {url}: {e}")
            return ""

    def create_documents_from_search(self, query: str, search_results: List[Dict]) -> List[Document]:
        """Convert search results to Haystack Documents."""
        documents = []

        for i, result in enumerate(search_results):
            title = result.get('title', 'No Title')
            url = result.get('link', '')
            snippet = result.get('snippet', '')

            # Try to extract full content
            full_content = self.extract_content_from_url(url)

            # Use full content if available, otherwise use snippet
            content = full_content if full_content else snippet

            if content and len(content.strip()) > 50:  # Ensure meaningful content
                doc = Document(
                    content=content,
                    meta={
                        "title": title,
                        "url": url,
                        "source": "web_search",
                        "query": query,
                        "search_rank": i + 1,
                        "timestamp": time.time()
                    }
                )
                documents.append(doc)

            # Add small delay to be respectful to websites
            time.sleep(0.5)

        return documents

    def search_and_create_docs(self, query: str, num_results: int = 5) -> List[Document]:
        """Complete pipeline: search web and create documents."""
        search_results = self.search_web(query, num_results)
        if not search_results:
            return []

        documents = self.create_documents_from_search(query, search_results)
        return documents

# Test function
if __name__ == "__main__":
    # Test without API key (will show warning)
    web_search = WebSearchQA()

    # Test search
    results = web_search.search_web("LeBron James latest news", 3)
    print(f"Found {len(results)} search results")

    if results:
        # Test content extraction
        docs = web_search.create_documents_from_search("LeBron James latest news", results[:1])
        print(f"Created {len(docs)} documents")
        if docs:
            print(f"Sample content: {docs[0].content[:200]}...")