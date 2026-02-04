from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from modules.utils import (
    get_logger, get_config,
    TextChunker, DocumentLoader, EmbeddingProvider, VectorStore
)
from modules.utils.chunking import Chunk

logger = get_logger(__name__)

@dataclass
class IndexingResult:
    total_documents: int
    total_chunks: int
    total_embeddings: int
    success_count: int
    error_count: int
    metadata: Dict[str, Any] = None

class IndexingPipeline:
    def __init__(self,
                 config: Optional[Any] = None,
                 embeddings: Optional[EmbeddingProvider] = None,
                 vector_store: Optional[VectorStore] = None,
                 chunker: Optional[TextChunker] = None):
        self.config = config or get_config()
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.chunker = chunker or TextChunker(
            chunk_size=self.config.get("retriever.chunk_size", 512),
            overlap=self.config.get("retriever.chunk_overlap", 50)
        )
        self.logger = get_logger(__name__)

    def index_documents(self, documents: List[Dict[str, Any]]) -> IndexingResult:
        result = IndexingResult(
            total_documents=len(documents),
            total_chunks=0,
            total_embeddings=0,
            success_count=0,
            error_count=0
        )

        try:
            chunks = self.chunker.chunk_documents(documents)
            result.total_chunks = len(chunks)
            self.logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")

            if not self.embeddings or not self.vector_store:
                self.logger.warning("Embeddings or vector store not configured")
                return result

            vectors_to_upsert = []
            for chunk in chunks:
                try:
                    embedding = self.embeddings.embed_text(chunk.content)

                    metadata = chunk.metadata or {}
                    metadata.update({
                        "chunk_id": chunk.chunk_id,
                        "source": chunk.source,
                        "start_index": chunk.start_index,
                        "end_index": chunk.end_index,
                        "content": chunk.content[:500]
                    })

                    vectors_to_upsert.append((chunk.chunk_id, embedding, metadata))
                    result.total_embeddings += 1
                except Exception as e:
                    self.logger.error(f"Error embedding chunk {chunk.chunk_id}: {e}")
                    result.error_count += 1

            if vectors_to_upsert:
                success = self.vector_store.upsert(vectors_to_upsert)
                if success:
                    result.success_count = result.total_embeddings
                    self.logger.info(f"Successfully indexed {result.success_count} chunks")
                else:
                    result.error_count = result.total_embeddings

        except Exception as e:
            self.logger.error(f"Error in indexing pipeline: {e}")
            result.error_count += 1

        return result

    def index_from_directory(self, directory_path: str, loader: DocumentLoader) -> IndexingResult:
        try:
            documents = loader.load(directory_path)
            return self.index_documents(documents)
        except Exception as e:
            self.logger.error(f"Error indexing from directory: {e}")
            return IndexingResult(
                total_documents=0,
                total_chunks=0,
                total_embeddings=0,
                success_count=0,
                error_count=1
            )

    def index_from_file(self, file_path: str, loader: DocumentLoader) -> IndexingResult:
        try:
            documents = loader.load(file_path)
            return self.index_documents(documents)
        except Exception as e:
            self.logger.error(f"Error indexing from file: {e}")
            return IndexingResult(
                total_documents=0,
                total_chunks=0,
                total_embeddings=0,
                success_count=0,
                error_count=1
            )
