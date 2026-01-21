from typing import List, Dict, Any
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import to_tsvector

from app.models import DocumentChunk, Document
from app.embeddings.service import EmbeddingService

logger = logging.getLogger(__name__)


class HybridRetriever:

    def __init__(self, db_session: AsyncSession, embedding_service: EmbeddingService):
        self.db = db_session
        self.embedding_service = embedding_service

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:

        vector_results = await self._vector_search(query, top_k)

        keyword_results = await self._keyword_search(query, top_k)

        combined = self._combine_results(
            vector_results,
            keyword_results,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight
        )

        filtered = [r for r in combined if r.get("score", 0) >= similarity_threshold]

        return sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)[:top_k]

    async def _vector_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        try:
            results = await self.embedding_service.search(query, top_k=top_k * 2)

            enriched_results = []
            for result in results:
                chunk_id = result.get("metadata", {}).get("chunk_id")
                if chunk_id:
                    result_obj = await self.db.execute(
                        select(DocumentChunk).where(DocumentChunk.id == chunk_id)
                    )
                    chunk = result_obj.scalar_one_or_none()
                    if chunk:
                        enriched_results.append({
                            "chunk_id": str(chunk.id),
                            "document_id": str(chunk.document_id),
                            "content": chunk.content,
                            "score": result.get("score", 0),
                            "source": "vector"
                        })

            return enriched_results
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            return []

    async def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        try:
            keywords = query.split()

            result = await self.db.execute(
                select(DocumentChunk, func.similarity(DocumentChunk.content, query).label("similarity"))
                .order_by(func.similarity(DocumentChunk.content, query).desc())
                .limit(top_k * 2)
            )
            chunks = result.all()

            results = []
            for chunk, similarity in chunks:
                results.append({
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "content": chunk.content,
                    "score": float(similarity) if similarity else 0,
                    "source": "keyword"
                })

            return results
        except Exception as e:
            logger.error(f"Keyword search error: {str(e)}")
            return []

    def _combine_results(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:

        combined = {}

        for result in vector_results:
            chunk_id = result["chunk_id"]
            score = result.get("score", 0) * vector_weight
            if chunk_id not in combined:
                combined[chunk_id] = {
                    "chunk_id": chunk_id,
                    "document_id": result["document_id"],
                    "content": result["content"],
                    "score": 0,
                    "sources": []
                }
            combined[chunk_id]["score"] += score
            combined[chunk_id]["sources"].append("vector")

        for result in keyword_results:
            chunk_id = result["chunk_id"]
            score = result.get("score", 0) * keyword_weight
            if chunk_id not in combined:
                combined[chunk_id] = {
                    "chunk_id": chunk_id,
                    "document_id": result["document_id"],
                    "content": result["content"],
                    "score": 0,
                    "sources": []
                }
            combined[chunk_id]["score"] += score
            if "keyword" not in combined[chunk_id]["sources"]:
                combined[chunk_id]["sources"].append("keyword")

        return list(combined.values())

    async def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        try:
            from sentence_transformers import CrossEncoder

            cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')

            pairs = [[query, result["content"]] for result in results]
            scores = cross_encoder.predict(pairs)

            for result, score in zip(results, scores):
                result["reranked_score"] = float(score)

            return sorted(results, key=lambda x: x.get("reranked_score", 0), reverse=True)
        except Exception as e:
            logger.error(f"Reranking error: {str(e)}")
            return results
