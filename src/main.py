import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import List
from src.crawler import WebCrawler
from src.chatgpt_client import ChatGPTClient
from src.config import settings

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI()
crawler = WebCrawler()
chatgpt_client = ChatGPTClient()

class AnalysisRequest(BaseModel):
    url: HttpUrl

class AnalysisResponse(BaseModel):
    insights: List[str]

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_website(request: AnalysisRequest) -> AnalysisResponse:
    """
    Endpoint to analyze a website using the crawler and ChatGPT.
    """
    try:
        # Crawl and extract content
        content = crawler.crawl(str(request.url))
        
        # Process with ChatGPT
        insights = chatgpt_client.process_content(content)
        
        return AnalysisResponse(insights=insights)
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}