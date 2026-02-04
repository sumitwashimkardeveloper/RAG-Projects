from typing import Optional, Dict, Any
from modules.utils import get_logger, get_config, get_vector_store, VectorStoreConfig

logger = get_logger(__name__)

class DatabaseManager:
    def __init__(self, config=None):
        self.config = config or get_config()
        self.vector_store = None
        self._initialize_vector_store()

    def _initialize_vector_store(self):
        try:
            vector_db_config = self.config.get_section("vector_db")
            index_name = vector_db_config.get("index_name", "agentic-rag")
            dimension = vector_db_config.get("dimension", 1536)
            metric = vector_db_config.get("metric", "cosine")
            provider = vector_db_config.get("provider", "pinecone")

            config = VectorStoreConfig(
                index_name=index_name,
                dimension=dimension,
                metric=metric
            )

            self.vector_store = get_vector_store(provider, config)
            logger.info(f"Initialized {provider} vector store: {index_name}")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.vector_store = None

    def get_vector_store(self):
        return self.vector_store

    def health_check(self) -> Dict[str, Any]:
        status = {
            "vector_store": "unavailable",
            "connected": False
        }

        if self.vector_store and self.vector_store.exists():
            status["vector_store"] = "available"
            status["connected"] = True

        return status

    def close(self):
        if self.vector_store:
            logger.info("Closing vector store connection")

_db_manager = None

def get_database_manager(config=None) -> DatabaseManager:
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(config)
    return _db_manager
