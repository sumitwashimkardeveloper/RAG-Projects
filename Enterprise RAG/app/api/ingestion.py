"""
Ingestion API Endpoints
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.ingestion import IngestionService
from app.connectors import ConfluenceConnector, NotionConnector, FileConnector

router = APIRouter(prefix="/api/v1/ingestion", tags=["Ingestion"])


class IngestionRequest:
    """Request models for ingestion"""

    def __init__(self):
        pass


@router.post("/sources", status_code=201)
async def create_data_source(
    name: str,
    source_type: str,
    config: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new data source connection

    Args:
        name: Human-readable source name
        source_type: Type of source (confluence, notion, file, etc.)
        config: Source-specific configuration (API keys, URLs, etc.)

    Returns:
        Created data source details
    """
    try:
        service = IngestionService(db)
        source = await service.create_data_source(name, source_type, config)
        await db.commit()

        return {
            "id": str(source.id),
            "name": source.name,
            "type": source.type,
            "is_active": source.is_active,
            "created_at": source.created_at.isoformat(),
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sources")
async def list_data_sources(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    List all data sources

    Args:
        active_only: Only return active sources

    Returns:
        List of data sources
    """
    try:
        service = IngestionService(db)
        sources = await service.list_data_sources(active_only=active_only)

        return [
            {
                "id": str(source.id),
                "name": source.name,
                "type": source.type,
                "is_active": source.is_active,
                "last_synced_at": source.last_synced_at.isoformat() if source.last_synced_at else None,
                "sync_status": source.sync_status,
            }
            for source in sources
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sources/{source_id}/sync")
async def sync_data_source(
    source_id: str,
    incremental: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """
    Synchronize documents from a data source

    Args:
        source_id: ID of data source to sync
        incremental: Only fetch changes since last sync

    Returns:
        Sync results
    """
    try:
        service = IngestionService(db)
        source = await service.get_data_source(source_id)

        if not source:
            raise HTTPException(status_code=404, detail="Data source not found")

        # Create connector based on source type
        connector_map = {
            "confluence": ConfluenceConnector,
            "notion": NotionConnector,
            "file": FileConnector,
        }

        ConnectorClass = connector_map.get(source.type)
        if not ConnectorClass:
            raise HTTPException(status_code=400, detail=f"Unknown source type: {source.type}")

        connector = ConnectorClass(source.config)

        # Perform sync
        result = await service.sync_data_source(
            source_id,
            connector,
            incremental=incremental,
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents(
    source_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    List ingested documents

    Args:
        source_id: Filter by data source
        skip: Number of records to skip
        limit: Maximum records to return

    Returns:
        List of documents
    """
    from sqlalchemy import select

    try:
        from app.models import Document

        query = select(Document)

        if source_id:
            query = query.where(Document.source_id == source_id)

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        documents = result.scalars().all()

        return [
            {
                "id": str(doc.id),
                "title": doc.title,
                "source_type": doc.source_type,
                "is_processed": doc.is_processed,
                "is_embedded": doc.is_embedded,
                "created_at": doc.created_at.isoformat(),
            }
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/{document_id}/chunk")
async def chunk_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Chunk a document into segments for embedding

    Args:
        document_id: ID of document to chunk

    Returns:
        Number of chunks created
    """
    try:
        service = IngestionService(db)
        chunks = await service.chunk_document(document_id)
        await db.commit()

        return {
            "document_id": document_id,
            "chunks_created": len(chunks),
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def ingestion_status(
    db: AsyncSession = Depends(get_db),
):
    """
    Get ingestion pipeline status

    Returns:
        Pipeline statistics
    """
    from sqlalchemy import select, func
    from app.models import Document, DocumentChunk, DataSource

    try:
        # Count documents
        result = await db.execute(select(func.count(Document.id)))
        total_docs = result.scalar() or 0

        # Count chunks
        result = await db.execute(select(func.count(DocumentChunk.id)))
        total_chunks = result.scalar() or 0

        # Count processed
        result = await db.execute(
            select(func.count(Document.id)).where(Document.is_processed == True)
        )
        processed_docs = result.scalar() or 0

        # Count embedded
        result = await db.execute(
            select(func.count(Document.id)).where(Document.is_embedded == True)
        )
        embedded_docs = result.scalar() or 0

        # Count data sources
        result = await db.execute(select(func.count(DataSource.id)))
        total_sources = result.scalar() or 0

        return {
            "total_documents": total_docs,
            "processed_documents": processed_docs,
            "embedded_documents": embedded_docs,
            "total_chunks": total_chunks,
            "total_sources": total_sources,
            "processing_rate": f"{(processed_docs / total_docs * 100):.1f}%" if total_docs > 0 else "0%",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
