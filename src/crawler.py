import requests
from bs4 import BeautifulSoup
import logging
import time
from typing import Dict, Optional
from .config import settings

class RateLimiter:
    def __init__(self, calls_per_minute):
        self.calls_per_minute = calls_per_minute
        self.last_call = 0

    def __enter__(self):
        if self.last_call > 0:
            elapsed = time.time() - self.last_call
            min_interval = 60.0 / self.calls_per_minute
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.last_call = time.time()

class WebCrawler:
    def __init__(self):
        self.rate_limiter = RateLimiter(settings.RATE_LIMIT)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; CustomBot/1.0; +http://example.com)'
        })

    def sanitize_url(self, url: str) -> str:
        """Validate and sanitize the input URL."""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return url

    def crawl(self, url: Optional[str] = None) -> Dict[str, str]:
        """Crawl the specified website and extract relevant content."""
        try:
            target_url = self.sanitize_url(url or settings.TARGET_URL)
            with self.rate_limiter:
                response = self.session.get(target_url, timeout=10)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract relevant content (customize based on target website)
            content = {
                'title': soup.title.string if soup.title else '',
                'main_content': ' '.join([p.get_text() for p in soup.find_all('p')]),
                'headers': ' '.join([h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])])
            }
            
            return self.process_content(content)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error crawling {url}: {str(e)}")
            raise

    def process_content(self, content: Dict[str, str]) -> Dict[str, str]:
        """Process and clean the crawled content."""
        processed = {}
        for key, value in content.items():
            # Remove extra whitespace and normalize text
            processed[key] = ' '.join(value.split())
        return processed