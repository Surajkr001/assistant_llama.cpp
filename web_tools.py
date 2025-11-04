"""
WebTools - Web search and data retrieval utilities
Provides internet access for information gathering
"""

import logging
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import json
import urllib.parse


class WebTools:
    """
    Web utilities for searching and fetching online information
    Supports DuckDuckGo search and webpage content extraction
    """
    
    def __init__(self, config: Dict):
        """
        Initialize web tools with configuration
        
        Args:
            config: Dictionary containing web configuration parameters
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('user_agent', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        })
        self.timeout = config.get('timeout', 10)
        self.max_results = config.get('max_results', 5)
        
        self.logger = logging.getLogger(__name__)
    
    def search(self, query: str, max_results: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Search the web for information
        
        Args:
            query: Search query
            max_results: Maximum number of results (uses config default if None)
            
        Returns:
            List of search results with title, url, and snippet
        """
        if max_results is None:
            max_results = self.max_results
        
        search_engine = self.config.get('search_engine', 'duckduckgo')
        
        try:
            if search_engine == 'duckduckgo':
                return self._search_duckduckgo(query, max_results)
            else:
                self.logger.warning(f"Unknown search engine: {search_engine}, using DuckDuckGo")
                return self._search_duckduckgo(query, max_results)
                
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """
        Search using DuckDuckGo HTML interface
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        try:
            # Use DuckDuckGo HTML version for scraping
            url = "https://html.duckduckgo.com/html/"
            data = {'q': query}
            
            response = self.session.post(url, data=data, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Parse search results
            for result_div in soup.find_all('div', class_='result')[:max_results]:
                try:
                    title_elem = result_div.find('a', class_='result__a')
                    snippet_elem = result_div.find('a', class_='result__snippet')
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        url = title_elem.get('href', '')
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                except Exception as e:
                    self.logger.debug(f"Error parsing result: {e}")
                    continue
            
            self.logger.info(f"Found {len(results)} search results for: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def fetch_webpage(self, url: str) -> Optional[str]:
        """
        Fetch and extract text content from a webpage
        
        Args:
            url: URL of the webpage
            
        Returns:
            str: Extracted text content, or None if failed
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            self.logger.info(f"Fetched {len(text)} characters from: {url}")
            return text
            
        except Exception as e:
            self.logger.error(f"Error fetching webpage: {e}")
            return None
    
    def fetch_webpage_summary(self, url: str, max_length: int = 500) -> Optional[str]:
        """
        Fetch and return a summary of webpage content
        
        Args:
            url: URL of the webpage
            max_length: Maximum length of summary
            
        Returns:
            str: Summary of webpage content
        """
        content = self.fetch_webpage(url)
        
        if content:
            if len(content) > max_length:
                return content[:max_length] + "..."
            return content
        
        return None
    
    def search_and_summarize(self, query: str) -> str:
        """
        Search for query and return formatted results with summaries
        
        Args:
            query: Search query
            
        Returns:
            str: Formatted search results
        """
        results = self.search(query)
        
        if not results:
            return f"No search results found for: {query}"
        
        summary = f"Search results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}\n"
            summary += f"   URL: {result['url']}\n"
            if result['snippet']:
                summary += f"   {result['snippet']}\n"
            summary += "\n"
        
        return summary.strip()
    
    def get_page_title(self, url: str) -> Optional[str]:
        """
        Get the title of a webpage
        
        Args:
            url: URL of the webpage
            
        Returns:
            str: Page title, or None if failed
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('title')
            
            return title.get_text(strip=True) if title else None
            
        except Exception as e:
            self.logger.error(f"Error getting page title: {e}")
            return None
    
    def download_file(self, url: str, filepath: str) -> bool:
        """
        Download a file from URL
        
        Args:
            url: URL of the file
            filepath: Local path to save the file
            
        Returns:
            bool: True if successful
        """
        try:
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.logger.info(f"Downloaded file to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading file: {e}")
            return False
    
    def check_url_accessible(self, url: str) -> bool:
        """
        Check if a URL is accessible
        
        Args:
            url: URL to check
            
        Returns:
            bool: True if accessible
        """
        try:
            response = self.session.head(url, timeout=self.timeout)
            return response.status_code < 400
        except:
            return False
    
    def shutdown(self):
        """Close the session and cleanup"""
        self.session.close()
        self.logger.info("Web tools session closed")


# Example usage
if __name__ == "__main__":
    import json
    
    logging.basicConfig(level=logging.INFO)
    
    # Load configuration
    with open("config.json", "r") as f:
        config = json.load(f)
    
    # Initialize web tools
    web = WebTools(config["web"])
    
    print("Testing web search...")
    print("="*60)
    
    # Test search
    query = "Python programming"
    print(f"\nSearching for: {query}")
    results = web.search(query, max_results=3)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   {result['url']}")
        print(f"   {result['snippet'][:100]}...")
    
    # Test search and summarize
    print("\n" + "="*60)
    print("\nSearch summary:")
    print(web.search_and_summarize("artificial intelligence"))
    
    # Cleanup
    web.shutdown()
