from openai import OpenAIError
import logging
from typing import List, Dict
from src.config import settings
from fastapi import HTTPException


class ChatGPTClient:
    def __init__(self):
        # Set the global API key for OpenAI
        openai.api_key = settings.OPENAI_API_KEY

    async def process_content(self, content: Dict[str, str]) -> List[str]:
        """
        Process content through ChatGPT and return insights.
        """
        try:
            prompt = f"""
Based on the following content:
Title: {content.get('title', 'No title')}
Headers: {content.get('headers', 'No headers')}
Main Content: {content.get('main_content', 'No content')}

Please provide exactly {settings.MAX_RESULTS} distinct, important insights or key points.
Format each point as a separate, concise statement.
"""
            response = await openai.ChatCompletion.acreate(
                model=settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            )
            insights = self._parse_response(response.choices[0].message.content)
            return insights[:settings.MAX_RESULTS]
        except OpenAIError as e:
            if 'insufficient_quota' in str(e):
                logging.error(f"OpenAI API quota exceeded: {str(e)}")
                raise HTTPException(
                    status_code=402,
                    detail="OpenAI API quota exceeded. Please check your billing details."
                )
            elif '429' in str(e):
                logging.error(f"OpenAI API rate limit exceeded: {str(e)}")
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )
            else:
                logging.error(f"OpenAI API error: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail="Error communicating with OpenAI API"
                )
        except Exception as e:
            logging.error(f"Error processing content with ChatGPT: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred while processing the content"
            )

    def _parse_response(self, response: str) -> List[str]:
        """Parse the ChatGPT response into a list of distinct insights."""
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        insights = [line.split('. ', 1)[-1] for line in lines if line]
        return insights
