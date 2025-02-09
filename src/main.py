import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
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
logger = logging.getLogger(__name__)

app = FastAPI()
crawler = WebCrawler()
chatgpt_client = ChatGPTClient()

class AnalysisRequest(BaseModel):
    urls: List[HttpUrl]

class AnalysisResponse(BaseModel):
    insights: List[str]

@app.websocket("/ws/analyze")
async def websocket_analyze(websocket: WebSocket):
    """WebSocket endpoint for analyzing multiple websites with continuation prompts."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            urls = data.get("urls", [])
            if not urls:
                await websocket.send_json({
                    "type": "error",
                    "message": "No URLs provided"
                })
                continue

            results = []
            try:
                crawled_contents = await crawler.crawl_multiple(urls, websocket)
                for content in crawled_contents:
                    # 非同期関数として await を追加
                    insights = await chatgpt_client.process_content(content)
                    results.append({
                        "url": content.get("url", ""),
                        "insights": insights
                    })
                await websocket.send_json({
                    "type": "complete",
                    "results": results
                })
            except Exception as e:
                logger.error(f"Error processing URLs: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": str(e)
                })
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "An unexpected error occurred"
            })
        except:
            pass

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_website(request: AnalysisRequest) -> AnalysisResponse:
    """
    REST endpoint to analyze a website using the crawler and ChatGPT.
    For single-URL analysis without continuation prompts.
    """
    try:
        content = await crawler.crawl(str(request.urls[0]))
        if not content or not any(content.values()):
            raise HTTPException(
                status_code=422,
                detail="Could not extract meaningful content from the provided URL"
            )
        # 非同期関数として await を追加
        insights = await chatgpt_client.process_content(content)
        if not insights:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate insights from the content"
            )
        return AnalysisResponse(insights=insights)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException as e:
        logger.error(f"HTTP error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY.startswith('your_'):
            return {"status": "error", "detail": "OpenAI API key not properly configured"}
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "error", "detail": str(e)}
