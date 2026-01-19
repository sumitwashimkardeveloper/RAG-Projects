"""
Data Ingestion Service - Orchestrates document ingestion pipeline
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models import DataSource, Document, SyncLog, SyncStatus, DocumentChunk
from app.connectors import BaseConnector, DocumentMetadata
from app.ingestion.chunking import DocumentChunker

logger = logging.getLogger(__name__)


class IngestionService:
    """
    Service for managing data source connections and document ingestion
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.chunker = DocumentChunker()

    async def create_data_source(
        self, name: str, source_type: str, config: Dict[str, Any]
    ) -> DataSource:
        """
        Create a new data source connection

        Args:
            name: Human-readable name
            source_type: Type of source (confluence, notion, file, etc.)
            config: Source-specific configuration

        Returns:
            Created DataSource object
        """
        try:
            data_source = DataSource(
                name=name,
                type=source_type,
                config=config,
                is_active=True,
            )
            self.db.add(data_source)
            await self.db.flush()
            logger.info(f"Created data source: {name} ({source_type})")
            return data_source
        except Exception as e:
            logger.error(f"Failed to create data source: {str(e)}")
            raise

    async def get_data_source(self, source_id: str) -> Optional[DataSource]:
        """Get a data source by ID"""
        result = await self.db.execute(
            select(DataSource).where(DataSource.id == source_id)
        )
        return result.scalar_one_or_none()

    async def list_data_sources(self, active_only: bool = True) -> List[DataSource]:
        """List all data sources"""
        query = select(DataSource)
        if active_only:
            query = query.where(DataSource.is_active == True)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def sync_data_source(
        self, source_id: str, connector: BaseConnector, incremental: bool = False
    ) -> Dict[str, Any]:
        """
        Synchronize documents from a data source

        Args:
            source_id: ID of data source to sync
            connector: Connector instance
            incremental: If True, only fetch updates since last sync

        Returns:
            Dictionary with sync results
        """
        source = await self.get_data_source(source_id)
        if not source:
            raise ValueError(f"Data source {source_id} not found")

        # Create sync log
        sync_log = SyncLog(
            data_source_id=source_id,
            status=SyncStatus.IN_PROGRESS.value,
        )
        self.db.add(sync_log)
        await self.db.flush()

        try:
            # Fetch documents from source
            if incremental and source.last_synced_at:
                logger.info(f"Fetching incremental updates from {source.name}")
                doc_metadata_list = connector.get_document_updates(source.last_synced_at)
            else:
                logger.info(f"Fetching all documents from {source.name}")
                doc_metadata_list = connector.get_documents()

            # Process each document
            created_count = 0
            updated_count = 0
            failed_count = 0

            for doc_metadata in doc_metadata_list:
                try:
                    result = await self._ingest_document(source_id, doc_metadata)
                    if result == "created":
                        created_count += 1
                    elif result == "updated":
                        updated_count += 1
                except Exception as e:
                    logger.error(
                        f"Failed to ingest document {doc_metadata.title}: {str(e)}"
                    )
                    failed_count += 1

            # Update sync log
            sync_log.status = SyncStatus.COMPLETED.value
            sync_log.completed_at = datetime.utcnow()
            sync_log.documents_processed = len(doc_metadata_list)
            sync_log.documents_created = created_count
            sync_log.documents_updated = updated_count
            sync_log.documents_failed = failed_count

            # Update data source
            await self.db.execute(
                update(DataSource)
                .where(DataSource.id == source_id)
                .values(
                    last_synced_at=datetime.utcnow(),
                    sync_status=SyncStatus.COMPLETED.value,
                )
            )

            await self.db.commit()

            logger.info(
                f"Sync completed for {source.name}: "
                f"Created={created_count}, Updated={updated_count}, Failed={failed_count}"
            )

            return {
                "source_id": str(source_id),
                "status": "completed",
                "documents_processed": len(doc_metadata_list),
                "documents_created": created_count,
                "documents_updated": updated_count,
                "documents_failed": failed_count,
            }

        except Exception as e:
            logger.error(f"Sync failed for {source.name}: {str(e)}")
            sync_log.status = SyncStatus.FAILED.value
            sync_log.error_message = str(e)
            sync_log.completed_at = datetime.utcnow()

            await self.db.execute(
                update(DataSource)
                .where(DataSource.id == source_id)
                .values(sync_status=SyncStatus.FAILED.value)
            )

            await self.db.commit()
            raise

    async def _ingest_document(self, source_id: str, doc_metadata: DocumentMetadata) -> str:
        """
        Ingest a single document

        Args:
            source_id: ID of data source
            doc_metadata: Document metadata from connector

        Returns:
            "created" or "updated"
        """
        # Check if document already exists
        result = await self.db.execute(
            select(Document).where(
                (Document.external_id == doc_metadata.source_url)
                | (Document.content_hash == self._hash_content(doc_metadata.content))
            )
        )
        existing_doc = result.scalar_one_or_none()

        if existing_doc:
            # Update existing document
            existing_doc.title = doc_metadata.title
            existing_doc.content = doc_metadata.content
            existing_doc.source_updated_at = doc_metadata.updated_at
            existing_doc.metadata = doc_metadata.metadata
            await self.db.flush()
            logger.debug(f"Updated document: {doc_metadata.title}")
            return "updated"
        else:
            # Create new document
            document = Document(
                title=doc_metadata.title,
                content=doc_metadata.content,
                source_type=doc_metadata.source_type,
                source_id=source_id,
                source_url=doc_metadata.source_url,
                author=doc_metadata.author,
                source_created_at=doc_metadata.created_at,
                source_updated_at=doc_metadata.updated_at,
                metadata=doc_metadata.metadata,
                content_hash=self._hash_content(doc_metadata.content),
            )
            self.db.add(document)
            await self.db.flush()
            logger.debug(f"Created document: {doc_metadata.title}")
            return "created"

    async def chunk_document(self, document_id: str) -> List[DocumentChunk]:
        """
        Split document into chunks for embedding

        Args:
            document_id: ID of document to chunk

        Returns:
            List of created DocumentChunk objects
        """
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Chunk the document
        chunks = self.chunker.chunk_text(
            document.content,
            chunk_size=1024,
            chunk_overlap=200,
        )

        # Create chunk records
        chunk_objects = []
        for idx, chunk_text in enumerate(chunks):
            chunk = DocumentChunk(
                document_id=document_id,
                content=chunk_text,
                chunk_index=idx,
            )
            chunk_objects.append(chunk)
            self.db.add(chunk)

        document.is_processed = True
        await self.db.flush()

        logger.info(f"Created {len(chunks)} chunks for document {document.title}")
        return chunk_objects

    @staticmethod
    def _hash_content(content: str) -> str:
        """Generate hash of content for deduplication"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
