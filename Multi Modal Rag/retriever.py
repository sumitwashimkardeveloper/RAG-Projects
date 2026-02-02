from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

from vector_store import VectorStore
from config import Config

@dataclass
class RetrievalResult:
    query: str
    documents: List[Dict[str, Any]]
    source_files: List[str]
    media_types: List[str]
    confidence_scores: List[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "documents": self.documents,
            "source_files": list(set(self.source_files)),
            "media_types": list(set(self.media_types)),
            "confidence_scores": self.confidence_scores
        }


class MultiModalRetriever:
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.config = Config()
        self.vector_store = vector_store or VectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        media_type_filter: Optional[str] = None
    ) -> RetrievalResult:

        if media_type_filter:
            results = self.vector_store.hybrid_search(query, media_type_filter, top_k)
        else:
            results = self.vector_store.similarity_search(query, top_k)

        source_files = list(set([r["metadata"]["file_path"] for r in results]))
        media_types = list(set([r["metadata"]["media_type"] for r in results]))
        confidence_scores = [r["similarity"] for r in results]

        return RetrievalResult(
            query=query,
            documents=results,
            source_files=source_files,
            media_types=media_types,
            confidence_scores=confidence_scores
        )

    def retrieve_by_media_type(
        self,
        query: str,
        media_type: str,
        top_k: int = 5
    ) -> RetrievalResult:

        return self.retrieve(query, top_k, media_type_filter=media_type)

    def retrieve_with_context(
        self,
        query: str,
        top_k: int = 5,
        context_expansion: int = 2
    ) -> Dict[str, Any]:

        results = self.vector_store.similarity_search(query, top_k)

        expanded_results = []

        for result in results:
            expanded_result = {
                "primary_result": result,
                "related_chunks": []
            }

            file_path = result["metadata"]["file_path"]
            chunk_index = result["metadata"]["chunk_index"]

            for doc in self.vector_store.list_all_documents():
                if (doc.file_path == file_path and
                    abs(doc.source_chunk_index - chunk_index) <= context_expansion and
                    doc.source_chunk_index != chunk_index):

                    expanded_result["related_chunks"].append({
                        "chunk_index": doc.source_chunk_index,
                        "content": doc.content,
                        "metadata": {
                            "media_type": doc.media_type,
                            "created_at": doc.created_at
                        }
                    })

            expanded_results.append(expanded_result)

        return {
            "query": query,
            "total_results": len(expanded_results),
            "results": expanded_results
        }

    def retrieve_multi_media_summary(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:

        results = self.vector_store.similarity_search(query, top_k)

        summary = {
            "query": query,
            "media_type_summaries": {}
        }

        media_type_results = {}

        for result in results:
            media_type = result["metadata"]["media_type"]
            if media_type not in media_type_results:
                media_type_results[media_type] = []
            media_type_results[media_type].append(result)

        for media_type, type_results in media_type_results.items():
            summary["media_type_summaries"][media_type] = {
                "count": len(type_results),
                "results": type_results,
                "combined_text": " ".join([r["content"] for r in type_results])
            }

        return summary

    def retrieve_by_file(
        self,
        file_path: str,
        query: Optional[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:

        all_docs = self.vector_store.list_all_documents()
        file_docs = [doc for doc in all_docs if doc.file_path == file_path]

        if not file_docs:
            return {"status": "error", "message": f"No documents found for file: {file_path}"}

        if query:
            doc_similarities = []
            query_embedding = self.vector_store.embedding_model.encode(query)

            import numpy as np
            for doc in file_docs:
                similarity = np.dot(query_embedding, doc.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(doc.embedding) + 1e-9
                )
                doc_similarities.append((doc, similarity))

            doc_similarities.sort(key=lambda x: x[1], reverse=True)
            file_docs = [doc for doc, _ in doc_similarities[:top_k]]

        return {
            "status": "success",
            "file_path": file_path,
            "total_chunks": len(file_docs),
            "chunks": [
                {
                    "index": doc.source_chunk_index,
                    "content": doc.content,
                    "metadata": {
                        "media_type": doc.media_type,
                        "created_at": doc.created_at
                    }
                } for doc in file_docs
            ]
        }

    def retrieve_cross_modal_relationships(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:

        results = self.vector_store.similarity_search(query, top_k * 2)

        relationships = {
            "query": query,
            "cross_modal_connections": []
        }

        file_mentions = {}
        for result in results:
            file_path = result["metadata"]["file_path"]
            if file_path not in file_mentions:
                file_mentions[file_path] = []
            file_mentions[file_path].append(result)

        for file_path, file_results in file_mentions.items():
            if len(file_results) > 1:
                relationships["cross_modal_connections"].append({
                    "file": file_path,
                    "result_count": len(file_results),
                    "results": file_results
                })

        return relationships

    def get_retrieval_statistics(self) -> Dict[str, Any]:
        stats = self.vector_store.get_statistics()

        return {
            "vector_store": stats,
            "retriever_info": {
                "embedding_model": self.config.EMBEDDING_MODEL,
                "embedding_dimension": self.config.EMBEDDING_DIMENSION
            }
        }
