from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import hashlib
from datetime import datetime

import numpy as np
from sentence_transformers import SentenceTransformer

from config import Config

@dataclass
class Document:
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    media_type: str
    file_path: str
    source_chunk_index: int
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "media_type": self.media_type,
            "file_path": self.file_path,
            "source_chunk_index": self.source_chunk_index,
            "created_at": self.created_at
        }


class VectorStore:
    def __init__(self, use_pinecone: bool = True):
        self.config = Config()
        self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        self.use_pinecone = use_pinecone
        self.local_store: Dict[str, Document] = {}

        if use_pinecone:
            try:
                import pinecone
                pinecone.init(
                    api_key=self.config.PINECONE_API_KEY,
                    environment=self.config.PINECONE_ENVIRONMENT
                )
                self.pinecone_index = pinecone.Index(self.config.PINECONE_INDEX_NAME)
                self.use_pinecone = True
            except Exception as e:
                print(f"Pinecone initialization failed: {e}. Using local storage.")
                self.use_pinecone = False

    def add_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        doc_ids = []

        for doc_data in documents:
            embedding = self.embedding_model.encode(doc_data["content"])
            doc_id = self._generate_doc_id(doc_data)

            doc = Document(
                id=doc_id,
                content=doc_data["content"],
                embedding=embedding.tolist(),
                metadata=doc_data.get("metadata", {}),
                media_type=doc_data.get("media_type", "unknown"),
                file_path=doc_data.get("file_path", ""),
                source_chunk_index=doc_data.get("chunk_index", 0),
                created_at=datetime.now().isoformat()
            )

            self.local_store[doc_id] = doc
            doc_ids.append(doc_id)

            if self.use_pinecone:
                self._upsert_to_pinecone(doc)

        return doc_ids

    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_model.encode(query)

        if self.use_pinecone:
            return self._search_pinecone(query_embedding, top_k)
        else:
            return self._search_local(query_embedding, top_k)

    def hybrid_search(
        self,
        query: str,
        media_type_filter: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_model.encode(query)

        results = self._search_local(query_embedding, top_k * 2)

        if media_type_filter:
            results = [r for r in results if r["metadata"]["media_type"] == media_type_filter]

        return results[:top_k]

    def _generate_doc_id(self, doc_data: Dict[str, Any]) -> str:
        content_hash = hashlib.md5(
            doc_data["content"].encode()
        ).hexdigest()[:8]

        file_path = doc_data.get("file_path", "")
        chunk_index = doc_data.get("chunk_index", 0)

        return f"{file_path.replace('/', '_')}_{chunk_index}_{content_hash}"

    def _search_local(
        self,
        query_embedding: np.ndarray,
        top_k: int
    ) -> List[Dict[str, Any]]:
        similarities = []

        for doc_id, doc in self.local_store.items():
            similarity = np.dot(query_embedding, doc.embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc.embedding) + 1e-9
            )
            similarities.append({
                "id": doc_id,
                "similarity": float(similarity),
                "content": doc.content,
                "metadata": {
                    "media_type": doc.media_type,
                    "file_path": doc.file_path,
                    "chunk_index": doc.source_chunk_index,
                    "created_at": doc.created_at,
                    **doc.metadata
                }
            })

        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]

    def _search_pinecone(
        self,
        query_embedding: List[float],
        top_k: int
    ) -> List[Dict[str, Any]]:
        try:
            results = self.pinecone_index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )

            formatted_results = []
            for match in results["matches"]:
                formatted_results.append({
                    "id": match["id"],
                    "similarity": float(match["score"]),
                    "content": match["metadata"].get("content", ""),
                    "metadata": match["metadata"]
                })

            return formatted_results
        except Exception as e:
            print(f"Pinecone search failed: {e}")
            return []

    def _upsert_to_pinecone(self, doc: Document):
        try:
            self.pinecone_index.upsert(
                vectors=[
                    (
                        doc.id,
                        doc.embedding,
                        {
                            "content": doc.content,
                            "media_type": doc.media_type,
                            "file_path": doc.file_path,
                            "chunk_index": doc.source_chunk_index,
                            "created_at": doc.created_at,
                            **doc.metadata
                        }
                    )
                ]
            )
        except Exception as e:
            print(f"Pinecone upsert failed: {e}")

    def delete_by_file_path(self, file_path: str) -> int:
        doc_ids_to_delete = [
            doc_id for doc_id, doc in self.local_store.items()
            if doc.file_path == file_path
        ]

        for doc_id in doc_ids_to_delete:
            del self.local_store[doc_id]

        if self.use_pinecone:
            try:
                self.pinecone_index.delete(ids=doc_ids_to_delete)
            except Exception as e:
                print(f"Pinecone delete failed: {e}")

        return len(doc_ids_to_delete)

    def get_document(self, doc_id: str) -> Optional[Document]:
        return self.local_store.get(doc_id)

    def list_all_documents(self) -> List[Document]:
        return list(self.local_store.values())

    def get_statistics(self) -> Dict[str, Any]:
        media_type_counts = {}
        total_chunks = 0

        for doc in self.local_store.values():
            media_type = doc.media_type
            media_type_counts[media_type] = media_type_counts.get(media_type, 0) + 1
            total_chunks += 1

        return {
            "total_documents": len(self.local_store),
            "total_chunks": total_chunks,
            "media_type_distribution": media_type_counts,
            "embedding_dimension": self.config.EMBEDDING_DIMENSION
        }
