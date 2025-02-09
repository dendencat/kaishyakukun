from typing import List
from dataclasses import dataclass
import configparser
import os

MAX_ALLOWED_URLS = 10  # Maximum number of URLs that can be crawled

@dataclass
class CrawlerConfig:
    urls: List[str]
    max_urls: int

    @classmethod
    def from_ini(cls, config_path: str = "config.ini") -> "CrawlerConfig":
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        config = configparser.ConfigParser()
        config.read(config_path)

        max_urls = config.getint("crawler", "max_urls", fallback=10)
        urls = [url.strip() for url in config.get("crawler", "urls").split("\n") if url.strip()]

        if len(urls) > max_urls:
            raise ValueError(f"Number of URLs ({len(urls)}) exceeds maximum allowed limit ({max_urls})")
        if len(urls) == 0:
            raise ValueError("At least one URL must be provided")

        return cls(urls=urls, max_urls=max_urls)
