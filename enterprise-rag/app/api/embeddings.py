from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.embeddings import (
    EmbeddingService,
    OpenAIEmbeddingProvider,
    PineconeVectorStore,
    WeaviateVectorStore
)
from app.config import settings

router = APIRouter(prefix="/api/v1/embeddings", tags=["Embeddings"])


class EmbedChunkRequest(BaseModel):
    chunk_id: str


class EmbedTextRequest(BaseModel):
    text: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10


class BatchEmbedRequest(BaseModel):
    chunk_ids: List[str]
    batch_size: int = 100


@router.post("/embed-chunk")
async def embed_chunk(
    request: EmbedChunkRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        provider = OpenAIEmbeddingProvider(settings.EMBEDDING_MODEL)
        vector_store = PineconeVectorStore()

        if not vector_store.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to vector store")

        service = EmbeddingService(db, provider, vector_store)
        success = await service.embed_chunk(request.chunk_id)

        if success:
            await db.commit()
            return {"status": "success", "chunk_id": request.chunk_id}
        else:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Failed to embed chunk")
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embed-text")
async def embed_text(request: EmbedTextRequest):
    try:
        provider = OpenAIEmbeddingProvider(settings.EMBEDDING_MODEL)
        embedding = provider.embed_text(request.text)

        return {
            "text": request.text[:100],
            "embedding_dimensions": len(embedding),
            "model": provider.model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-embed")
async def batch_embed(
    request: BatchEmbedRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        provider = OpenAIEmbeddingProvider(settings.EMBEDDING_MODEL)
        vector_store = PineconeVectorStore()

        if not vector_store.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to vector store")

        service = EmbeddingService(db, provider, vector_store)
        results = await service.embed_chunks_batch(
            request.chunk_ids,
            batch_size=request.batch_size
        )

        successful = sum(1 for v in results.values() if v)
        return {
            "status": "success",
            "total_chunks": len(results),
            "successful": successful,
            "failed": len(results) - successful
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search(
    request: SearchRequest,
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


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    try:
        provider = OpenAIEmbeddingProvider(settings.EMBEDDING_MODEL)
        vector_store = PineconeVectorStore()

        if not vector_store.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to vector store")

        service = EmbeddingService(db, provider, vector_store)
        stats = await service.get_embedding_stats()

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
