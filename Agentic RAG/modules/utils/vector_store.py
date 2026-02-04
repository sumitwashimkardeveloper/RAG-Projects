from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class VectorStoreConfig:
    index_name: str
    dimension: int
    metric: str = "cosine"

class VectorStore(ABC):
    @abstractmethod
    def upsert(self, vectors: List[Tuple[str, List[float], Dict[str, Any]]]) -> bool:
        pass

    @abstractmethod
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete(self, ids: List[str]) -> bool:
        pass

    @abstractmethod
    def exists(self) -> bool:
        pass

class PineconeVectorStore(VectorStore):
    def __init__(self, config: VectorStoreConfig):
        try:
            import pinecone
        except ImportError:
            raise ImportError("pinecone-client package required")

        self.config = config
        api_key = os.getenv("PINECONE_API_KEY")
        environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")

        if not api_key:
            logger.warning("PINECONE_API_KEY not set, using mock mode")
            self.index = None
            return

        try:
            pinecone.init(api_key=api_key, environment=environment)
            if config.index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=config.index_name,
                    dimension=config.dimension,
                    metric=config.metric
                )
            self.index = pinecone.Index(config.index_name)
            logger.info(f"Connected to Pinecone index: {config.index_name}")
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {e}")
            self.index = None

    def upsert(self, vectors: List[Tuple[str, List[float], Dict[str, Any]]]) -> bool:
        if not self.index:
            logger.warning("Pinecone index not available")
            return False

        try:
            vectors_to_upsert = []
            for vector_id, embedding, metadata in vectors:
                vectors_to_upsert.append((vector_id, embedding, metadata))

            self.index.upsert(vectors=vectors_to_upsert)
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
            return True
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            return False

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.index:
            logger.warning("Pinecone index not available")
            return []

        try:
            results = self.index.query(vector=query_vector, top_k=top_k, include_metadata=True)
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                }
                for match in results.matches
            ]
        except Exception as e:
            logger.error(f"Error searching Pinecone: {e}")
            return []

    def delete(self, ids: List[str]) -> bool:
        if not self.index:
            return False

        try:
            self.index.delete(ids=ids)
            return True
        except Exception as e:
            logger.error(f"Error deleting from Pinecone: {e}")
            return False

    def exists(self) -> bool:
        return self.index is not None

class WeaviateVectorStore(VectorStore):
    def __init__(self, config: VectorStoreConfig):
        try:
            import weaviate
        except ImportError:
            raise ImportError("weaviate-client package required")

        self.config = config
        url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        api_key = os.getenv("WEAVIATE_API_KEY")

        try:
            auth_client_secret = None
            if api_key:
                from weaviate.auth import Auth
                auth_client_secret = Auth.api_key.ApiKey(api_key)

            self.client = weaviate.Client(
                url=url,
                auth_client_secret=auth_client_secret
            )
            logger.info(f"Connected to Weaviate at {url}")
        except Exception as e:
            logger.error(f"Error initializing Weaviate: {e}")
            self.client = None

    def upsert(self, vectors: List[Tuple[str, List[float], Dict[str, Any]]]) -> bool:
        if not self.client:
            return False

        try:
            for vector_id, embedding, metadata in vectors:
                self.client.data_object.create(
                    data_object=metadata,
                    class_name=self.config.index_name,
                    vector=embedding
                )
            logger.info(f"Upserted {len(vectors)} vectors to Weaviate")
            return True
        except Exception as e:
            logger.error(f"Error upserting to Weaviate: {e}")
            return False

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.client:
            return []

        try:
            where_filter = {
                "path": ["vector"],
                "operator": "Equal",
                "valueVector": query_vector
            }

            results = self.client.query.get(
                self.config.index_name,
                ["*"]
            ).with_limit(top_k).do()

            return results.get("data", {}).get("Get", {}).get(self.config.index_name, [])
        except Exception as e:
            logger.error(f"Error searching Weaviate: {e}")
            return []

    def delete(self, ids: List[str]) -> bool:
        if not self.client:
            return False

        try:
            for doc_id in ids:
                self.client.data_object.delete(
                    uuid=doc_id,
                    class_name=self.config.index_name
                )
            return True
        except Exception as e:
            logger.error(f"Error deleting from Weaviate: {e}")
            return False

    def exists(self) -> bool:
        return self.client is not None

def get_vector_store(provider: str, config: VectorStoreConfig) -> VectorStore:
    if provider.lower() == "pinecone":
        return PineconeVectorStore(config)
    elif provider.lower() == "weaviate":
        return WeaviateVectorStore(config)
    else:
        raise ValueError(f"Unknown vector store provider: {provider}")
