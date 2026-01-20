"""
Batch Processing API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.processing.batch import BatchProcessingService

router = APIRouter(prefix="/api/v1/batch", tags=["Batch Processing"])


@router.post("/process-unprocessed")
async def process_unprocessed_documents(
    limit: int = 100,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    strategy: str = "semantic",
    db: AsyncSession = Depends(get_db),
):
    """
    Process all unprocessed documents in batch

    Args:
        limit: Maximum documents to process
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        strategy: Chunking strategy

    Returns:
        Processing statistics
    """
    try:
        service = BatchProcessingService(db)
        result = await service.process_unprocessed_documents(
            limit=limit,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
        )

        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/{document_id}")
async def process_single_document(
    document_id: str,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    strategy: str = "semantic",
    db: AsyncSession = Depends(get_db),
):
    """
    Process a single document

    Args:
        document_id: ID of document to process
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        strategy: Chunking strategy

    Returns:
        Number of chunks created
    """
    try:
        service = BatchProcessingService(db)
        chunks_created = await service.process_document(
            document_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
        )

        return {
            "document_id": document_id,
            "chunks_created": chunks_created,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reprocess/{document_id}")
async def reprocess_document(
    document_id: str,
    chunk_size: int = 1024,
    chunk_overlap: int = 200,
    strategy: str = "semantic",
    db: AsyncSession = Depends(get_db),
):
    """
    Reprocess a document (delete and recreate chunks)

    Args:
        document_id: ID of document to reprocess
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        strategy: Chunking strategy

    Returns:
        Number of chunks created
    """
    try:
        service = BatchProcessingService(db)
        chunks_created = await service.reprocess_document(
            document_id,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
        )

        return {
            "document_id": document_id,
            "chunks_created": chunks_created,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_processing_stats(db: AsyncSession = Depends(get_db)):
    """
    Get document processing statistics

    Returns:
        Processing statistics
    """
    try:
        service = BatchProcessingService(db)
        stats = await service.get_processing_stats()

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
