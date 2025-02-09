from pydantic import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    TARGET_URL: str = "https://example.com"
    MAX_RESULTS: int = 10
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()