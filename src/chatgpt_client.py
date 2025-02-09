from openai import OpenAI
import logging
from typing import List, Dict
from .config import settings

class ChatGPTClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def process_content(self, content: Dict[str, str]) -> List[str]:
        """
        Process content through ChatGPT and return exactly 10 insights.
        """
        try:
            # Prepare prompt with the content
            prompt = f"""
            Based on the following content:
            Title: {content['title']}
            Headers: {content['headers']}
            Main Content: {content['main_content']}
            
            Please provide exactly 10 distinct, important insights or key points.
            Format each point as a separate, concise statement.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )

            # Extract and process the response
            insights = self._parse_response(response.choices[0].message.content)
            return insights[:settings.MAX_RESULTS]  # Ensure exactly 10 results

        except Exception as e:
            logging.error(f"Error processing content with ChatGPT: {str(e)}")
            raise

    def _parse_response(self, response: str) -> List[str]:
        """Parse the ChatGPT response into a list of distinct insights."""
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        # Remove numbering and clean up the insights
        insights = [line.split('. ', 1)[-1] for line in lines if line]
        return insights