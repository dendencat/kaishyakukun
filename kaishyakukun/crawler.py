from .config import CrawlerConfig
import asyncio
from typing import List

class Crawler:
    def __init__(self, config_path: str = "config.ini"):
        self.config = CrawlerConfig.from_ini(config_path)

    async def crawl(self) -> List[dict]:
        results = []
        # Create tasks for each URL
        tasks = [self._crawl_url(url) for url in self.config.urls]
        # Run tasks concurrently
        results = await asyncio.gather(*tasks)
        return results

    async def _crawl_url(self, url: str) -> dict:
        # Implement the actual crawling logic for a single URL
        # ...existing crawling code...
        pass
