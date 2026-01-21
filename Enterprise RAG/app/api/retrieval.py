from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.retrieval import HybridRetriever
from app.embeddings import EmbeddingService, OpenAIEmbeddingProvider, PineconeVectorStore
from app.config import settings

router = APIRouter(prefix="/api/v1/retrieval", tags=["Retrieval"])


class RetrievalRequest(BaseModel):
    query: str
    top_k: int = 10
    vector_weight: float = 0.7
    keyword_weight: float = 0.3
    similarity_threshold: float = 0.5
    use_reranking: bool = False


class VectorSearchRequest(BaseModel):
    query: str
    top_k: int = 10


class KeywordSearchRequest(BaseModel):
    query: str
    top_k: int = 10


@router.post("/hybrid")
async def hybrid_search(
    request: RetrievalRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        provider = OpenAIEmbeddingProvider(settings.EMBEDDING_MODEL)
        vector_store = PineconeVectorStore()

        if not vector_store.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to vector store")

        embedding_service = EmbeddingService(db, provider, vector_store)
        retriever = HybridRetriever(db, embedding_service)

        results = await retriever.retrieve(
            request.query,
            top_k=request.top_k,
            vector_weight=request.vector_weight,
            keyword_weight=request.keyword_weight,
            similarity_threshold=request.similarity_threshold
        )

        if request.use_reranking:
            results = await retriever.rerank_results(request.query, results)

        return {
            "query": request.query,
            "results_count": len(results),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vector-search")
async def vector_search(
    request: VectorSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        provider = OpenAIEmbeddingProvider(settings.EMBEDDING_MODEL)
        vector_store = PineconeVectorStore()

        if not vector_store.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to vector store")

        service = EmbeddingService(db, provider, vector_store)
        results = await service.search(request.query, top_k=request.top_k)

        return {
            "query": request.query,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keyword-search")
async def keyword_search(
    request: KeywordSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.retrieval import HybridRetriever
        from app.embeddings import EmbeddingService, OpenAIEmbeddingProvider, PineconeVectorStore

        provider = OpenAIEmbeddingProvider(settings.EMBEDDING_MODEL)
        vector_store = PineconeVectorStore()
        embedding_service = EmbeddingService(db, provider, vector_store)
        retriever = HybridRetriever(db, embedding_service)

        results = await retriever._keyword_search(request.query, request.top_k)

        return {
            "query": request.query,
            "results_count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
