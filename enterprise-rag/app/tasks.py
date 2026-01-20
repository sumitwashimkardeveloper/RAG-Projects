"""
Celery Background Tasks
Handles asynchronous processing of documents and ingestion
"""

import logging
from datetime import datetime
from celery import Celery, current_task
from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "enterprise_rag",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=["json"],
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    result_expires=3600,  # 1 hour
)


# Database session factory for async tasks
async_engine = None
async_session_factory = None


def get_async_session():
    """Get async database session"""
    global async_engine, async_session_factory

    if not async_engine:
        async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
        )
        async_session_factory = sessionmaker(
            async_engine, class_=AsyncSession, expire_on_commit=False
        )

    return async_session_factory()


@celery_app.task(bind=True, name="process_document")
def process_document_task(self, document_id: str, chunk_size: int = 1024):
    """
    Asynchronously process a document for chunking

    Args:
        document_id: ID of document to process
        chunk_size: Target chunk size
    """
    try:
        current_task.update_state(
            state="PROCESSING", meta={"current": 0, "total": 1}
        )

        logger.info(f"Processing document {document_id}")

        # Import here to avoid circular imports
        from app.processing.batch import BatchProcessingService
        import asyncio

        async def process():
            session = get_async_session()
            try:
                service = BatchProcessingService(session)
                chunks = await service.process_document(
                    document_id, chunk_size=chunk_size
                )
                return {"status": "success", "chunks_created": chunks}
            finally:
                await session.close()

        result = asyncio.run(process())

        logger.info(f"Successfully processed document {document_id}")
        return result

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        raise


@celery_app.task(bind=True, name="batch_process_documents")
def batch_process_documents_task(self, limit: int = 100):
    """
    Batch process unprocessed documents

    Args:
        limit: Maximum documents to process in batch
    """
    try:
        current_task.update_state(
            state="PROCESSING", meta={"status": "Starting batch processing"}
        )

        logger.info(f"Starting batch processing of {limit} documents")

        # Import here to avoid circular imports
        from app.processing.batch import BatchProcessingService
        import asyncio

        async def process():
            session = get_async_session()
            try:
                service = BatchProcessingService(session)
                result = await service.process_unprocessed_documents(limit=limit)
                return result
            finally:
                await session.close()

        result = asyncio.run(process())

        logger.info(
            f"Batch processing completed: {result['documents_processed']} documents processed"
        )
        return result

    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise


@celery_app.task(bind=True, name="sync_data_source")
def sync_data_source_task(self, source_id: str, incremental: bool = False):
    """
    Asynchronously sync a data source

    Args:
        source_id: ID of data source to sync
        incremental: Only fetch updates since last sync
    """
    try:
        current_task.update_state(
            state="PROCESSING", meta={"status": "Starting data source sync"}
        )

        logger.info(f"Syncing data source {source_id}")

        # Import here to avoid circular imports
        from app.ingestion import IngestionService
        from app.connectors import (
            ConfluenceConnector,
            NotionConnector,
            FileConnector,
        )
        import asyncio

        async def sync():
            from app.database import get_db
            from sqlalchemy.ext.asyncio import AsyncSession

            session = get_async_session()
            try:
                service = IngestionService(session)
                source = await service.get_data_source(source_id)

                if not source:
                    raise ValueError(f"Data source {source_id} not found")

                # Get appropriate connector
                connector_map = {
                    "confluence": ConfluenceConnector,
                    "notion": NotionConnector,
                    "file": FileConnector,
                }

                ConnectorClass = connector_map.get(source.type)
                if not ConnectorClass:
                    raise ValueError(f"Unknown source type: {source.type}")

                connector = ConnectorClass(source.config)

                # Perform sync
                result = await service.sync_data_source(
                    source_id, connector, incremental=incremental
                )

                current_task.update_state(
                    state="PROCESSING",
                    meta={"status": "Sync completed", "result": result},
                )

                return result
            finally:
                await session.close()

        result = asyncio.run(sync())

        logger.info(f"Successfully synced data source {source_id}")
        return result

    except Exception as e:
        logger.error(f"Error syncing data source {source_id}: {str(e)}")
        raise


@celery_app.task(bind=True, name="reprocess_document")
def reprocess_document_task(self, document_id: str):
    """
    Reprocess a document with new chunking parameters

    Args:
        document_id: ID of document to reprocess
    """
    try:
        logger.info(f"Reprocessing document {document_id}")

        from app.processing.batch import BatchProcessingService
        import asyncio

        async def process():
            session = get_async_session()
            try:
                service = BatchProcessingService(session)
                chunks = await service.reprocess_document(document_id)
                return {"status": "success", "chunks_created": chunks}
            finally:
                await session.close()

        result = asyncio.run(process())

        logger.info(f"Successfully reprocessed document {document_id}")
        return result

    except Exception as e:
        logger.error(f"Error reprocessing document {document_id}: {str(e)}")
        raise


@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks"""
    # Process unprocessed documents every hour
    sender.add_periodic_task(
        3600.0, batch_process_documents_task.s(), name="Batch process documents hourly"
    )


@celery_app.task(bind=True, name="health_check")
def health_check_task(self):
    """Simple health check task"""
    return {"status": "healthy", "timestamp": str(datetime.utcnow())}
