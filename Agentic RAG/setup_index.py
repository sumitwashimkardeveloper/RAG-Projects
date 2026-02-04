import os
import sys
from pathlib import Path
from modules.utils import (
    get_logger, get_config, get_embeddings, get_vector_store,
    VectorStoreConfig, IndexingPipeline, DirectoryLoader, TextChunker
)

logger = get_logger(__name__, log_file=str(Path("logs") / "indexing.log"))

def setup_index(data_directory: str = "data"):
    try:
        logger.info("Starting index setup")

        config = get_config()

        embedding_provider = config.get("llm.provider", "openai")
        embeddings = get_embeddings(provider=embedding_provider)

        vector_db_config = config.get_section("vector_db")
        vector_store_config = VectorStoreConfig(
            index_name=vector_db_config.get("index_name", "agentic-rag"),
            dimension=vector_db_config.get("dimension", 1536),
            metric=vector_db_config.get("metric", "cosine")
        )

        vector_store_provider = vector_db_config.get("provider", "pinecone")
        vector_store = get_vector_store(vector_store_provider, vector_store_config)

        chunker = TextChunker(
            chunk_size=config.get("retriever.chunk_size", 512),
            overlap=config.get("retriever.chunk_overlap", 50)
        )

        pipeline = IndexingPipeline(
            config=config,
            embeddings=embeddings,
            vector_store=vector_store,
            chunker=chunker
        )

        logger.info(f"Using embedding provider: {embedding_provider}")
        logger.info(f"Using vector store provider: {vector_store_provider}")

        data_path = Path(data_directory)
        if not data_path.exists():
            logger.warning(f"Data directory not found: {data_directory}")
            logger.info("Creating sample data directory")
            data_path.mkdir(parents=True, exist_ok=True)
            return

        loader = DirectoryLoader()
        result = pipeline.index_from_directory(str(data_path), loader)

        logger.info(f"Indexing complete:")
        logger.info(f"  Total documents: {result.total_documents}")
        logger.info(f"  Total chunks: {result.total_chunks}")
        logger.info(f"  Total embeddings: {result.total_embeddings}")
        logger.info(f"  Success count: {result.success_count}")
        logger.info(f"  Error count: {result.error_count}")

        return result

    except Exception as e:
        logger.error(f"Error during index setup: {e}")
        raise

if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    setup_index(data_dir)
