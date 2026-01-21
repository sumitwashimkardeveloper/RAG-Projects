from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
import logging

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):

    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 2048):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        pass

    @abstractmethod
    async def generate_async(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        pass

    @abstractmethod
    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncIterator[str]:
        pass

    def format_messages(
        self,
        system_prompt: str,
        user_query: str,
        context: List[str] = None,
        chat_history: List[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if chat_history:
            messages.extend(chat_history)

        if context:
            context_text = "\n\n".join(context)
            context_message = f"Context:\n{context_text}\n\nQuestion: {user_query}"
        else:
            context_message = user_query

        messages.append({"role": "user", "content": context_message})

        return messages

    def estimate_tokens(self, text: str) -> int:
        return len(text.split()) * 1.3
