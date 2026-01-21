from typing import List, Dict, Optional, AsyncIterator
import logging
import anthropic

from app.llm.base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)


class AnthropicLLMProvider(BaseLLMProvider):

    def __init__(self, model: str = None, temperature: float = 0.7, max_tokens: int = 2048):
        super().__init__(model or settings.ANTHROPIC_MODEL, temperature, max_tokens)
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.async_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        try:
            system = None
            filtered_messages = []

            for msg in messages:
                if msg.get("role") == "system":
                    system = msg.get("content")
                else:
                    filtered_messages.append(msg)

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                system=system,
                messages=filtered_messages,
                temperature=temperature or self.temperature
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic generation error: {str(e)}")
            raise

    async def generate_async(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        try:
            system = None
            filtered_messages = []

            for msg in messages:
                if msg.get("role") == "system":
                    system = msg.get("content")
                else:
                    filtered_messages.append(msg)

            response = await self.async_client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                system=system,
                messages=filtered_messages,
                temperature=temperature or self.temperature
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic async generation error: {str(e)}")
            raise

    async def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[str]:
        try:
            system = None
            filtered_messages = []

            for msg in messages:
                if msg.get("role") == "system":
                    system = msg.get("content")
                else:
                    filtered_messages.append(msg)

            with self.client.messages.stream(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                system=system,
                messages=filtered_messages,
                temperature=temperature or self.temperature
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic streaming error: {str(e)}")
            raise

    def count_tokens(self, text: str) -> int:
        try:
            response = self.client.messages.count_tokens(
                model=self.model,
                messages=[{"role": "user", "content": text}]
            )
            return response.input_tokens
        except Exception as e:
            logger.warning(f"Token counting failed: {str(e)}")
            return self.estimate_tokens(text)
