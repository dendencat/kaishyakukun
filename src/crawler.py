import requests
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
import time
from typing import Dict, Optional, List
from fastapi import HTTPException, WebSocket
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
        self.session = None
        self.websocket: Optional[WebSocket] = None
        self.processed_urls: List[str] = []
        self.remaining_urls: List[str] = []

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                'User-Agent': 'Mozilla/5.0 (compatible; CustomBot/1.0; +http://example.com)'
            })
        return self.session

    def sanitize_url(self, url: str) -> str:
        """Validate and sanitize the input URL."""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return url

    async def crawl_multiple(self, urls: List[str], websocket: WebSocket) -> List[Dict[str, str]]:
        """Crawl multiple URLs with confirmation between each."""
        self.websocket = websocket
        self.processed_urls = []
        self.remaining_urls = urls.copy()
        results = []
        
        for i, url in enumerate(urls, 1):
            # Update URL tracking
            self.remaining_urls = urls[i:]
            
            # Crawl current URL
            result = await self.crawl(url)
            self.processed_urls.append(url)
            results.append(result)
            
            # If not the last URL, ask for continuation
            if i < len(urls):
                continue_crawling = await self.ask_continuation()
                if not continue_crawling:
                    # Send final status before breaking
                    await self.websocket.send_json({
                        "type": "status",
                        "message": "クローリングを中止しました。",  # "Crawling stopped."
                        "processed": len(self.processed_urls),
                        "remaining": len(self.remaining_urls) - 1
                    })
                    break
                
        return results

    async def ask_continuation(self) -> bool:
        """Ask user if they want to continue to the next URL."""
        if self.websocket:
            await self.websocket.send_json({
                "type": "confirmation",
                "message": "続行: '反復処理を続行しますか?'",
                "current_status": {
                    "processed_urls": len(self.processed_urls),
                    "remaining_urls": len(self.remaining_urls) - 1,
                    "last_processed": self.processed_urls[-1] if self.processed_urls else None,
                    "next_url": self.remaining_urls[0] if self.remaining_urls else None
                }
            })
            response = await self.websocket.receive_json()
            return response.get("continue", False)
        return True

    async def crawl(self, url: Optional[str] = None) -> Dict[str, str]:
        """Crawl the specified website and extract relevant content."""
        try:
            target_url = self.sanitize_url(url or settings.TARGET_URL)
            session = await self.get_session()

            async with session.get(target_url, timeout=10) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to fetch content from {target_url}"
                    )
                html = await response.text()

            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract relevant content
            content = {
                'url': target_url,  # Add URL to content for reference
                'title': soup.title.string if soup.title else '',
                'main_content': ' '.join([p.get_text() for p in soup.find_all('p')]),
                'headers': ' '.join([h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])])
            }
            
            return self.process_content(content)
            
        except aiohttp.ClientError as e:
            logging.error(f"Network error crawling {url}: {str(e)}")
            raise HTTPException(status_code=502, detail=f"Failed to fetch content: {str(e)}")
        except Exception as e:
            logging.error(f"Error crawling {url}: {str(e)}")
            raise

    def process_content(self, content: Dict[str, str]) -> Dict[str, str]:
        """Process and clean the crawled content."""
        processed = {}
        for key, value in content.items():
            if not isinstance(value, str):
                logging.warning(f"Unexpected type for {key}: {type(value)}")
                value = str(value)
            # Remove extra whitespace and normalize text
            processed[key] = ' '.join(value.split())
        return processed

    async def __aenter__(self):
        await self.get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None