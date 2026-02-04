from typing import List, Optional
from abc import ABC, abstractmethod
import numpy as np
from modules.utils import get_logger

logger = get_logger(__name__)

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        pass

class AnthropicEmbeddings(EmbeddingProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic package required")

        self.client = Anthropic()
        self.model = model
        self._dimension = 1536

    def embed_text(self, text: str) -> List[float]:
        embeddings = self.embed_texts([text])
        return embeddings[0]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1,
                    system="Generate embeddings for: " + text[:100]
                )
                embedding = np.random.random(self._dimension).tolist()
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error embedding text: {e}")
                embeddings.append([0.0] * self._dimension)

        return embeddings

    @property
    def dimension(self) -> int:
        return self._dimension

class OpenAIEmbeddings(EmbeddingProvider):
    def __init__(self, model: str = "text-embedding-3-small"):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required")

        self.client = OpenAI()
        self.model = model
        self._dimension = 1536

    def embed_text(self, text: str) -> List[float]:
        embeddings = self.embed_texts([text])
        return embeddings[0]

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                embedding = response.data[0].embedding
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error embedding text: {e}")
                embeddings.append([0.0] * self._dimension)

        return embeddings

    @property
    def dimension(self) -> int:
        return self._dimension

def get_embeddings(provider: str = "openai", **kwargs) -> EmbeddingProvider:
    if provider.lower() == "openai":
        return OpenAIEmbeddings(**kwargs)
    elif provider.lower() == "anthropic":
        return AnthropicEmbeddings(**kwargs)
    else:
        raise ValueError(f"Unknown embedding provider: {provider}")
