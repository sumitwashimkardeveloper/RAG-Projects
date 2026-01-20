"""
Batch Processing for Document Chunking
Integrates with ingestion service to process documents in bulk
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Document, DocumentChunk
from app.processing import TextProcessor

logger = logging.getLogger(__name__)


class BatchProcessingService:
    """
    Process documents in batch for efficiency
    Handles chunking, tokenization, and metadata enrichment
    """

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.processor = TextProcessor()

    async def process_unprocessed_documents(
        self,
        limit: int = 100,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
        strategy: str = "semantic",
    ) -> Dict[str, Any]:
        """
        Process all unprocessed documents

        Args:
            limit: Maximum documents to process
            chunk_size: Target chunk size
            chunk_overlap: Overlap between chunks
            strategy: Chunking strategy

        Returns:
            Processing statistics
        """
        # Get unprocessed documents
        result = await self.db.execute(
            select(Document)
            .where(Document.is_processed == False)
            .limit(limit)
        )
        documents = result.scalars().all()

        if not documents:
            logger.info("No unprocessed documents found")
            return {
                "status": "success",
                "documents_processed": 0,
                "chunks_created": 0,
            }

        total_chunks = 0
        failed_count = 0

        for doc in documents:
            try:
                chunks_created = await self._process_document(
                    doc,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    strategy=strategy,
                )
                total_chunks += chunks_created
            except Exception as e:
                logger.error(f"Error processing document {doc.id}: {str(e)}")
                failed_count += 1

        await self.db.commit()

        logger.info(
            f"Processed {len(documents)} documents, created {total_chunks} chunks"
        )

        return {
            "status": "success",
            "documents_processed": len(documents),
            "chunks_created": total_chunks,
            "failed_documents": failed_count,
        }

    async def process_document(
        self,
        document_id: str,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
        strategy: str = "semantic",
    ) -> int:
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
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document {document_id} not found")

        chunks_created = await self._process_document(
            document,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
        )

        await self.db.commit()
        return chunks_created

    async def _process_document(
        self,
        document: Document,
        chunk_size: int,
        chunk_overlap: int,
        strategy: str,
    ) -> int:
        """Internal method to process a document"""
        # Update processor settings
        self.processor.chunk_size = chunk_size
        self.processor.chunk_overlap = chunk_overlap

        # Process text
        result = self.processor.process(document.content, strategy=strategy)

        if not result.chunks:
            logger.warning(f"No chunks created for document {document.id}")
            document.is_processed = True
            return 0

        # Create chunk records
        chunk_objects = []
        for idx, chunk_text in enumerate(result.chunks):
            chunk = DocumentChunk(
                document_id=document.id,
                content=chunk_text,
                chunk_index=idx,
                token_count=result.metadata["token_distribution"][idx]
                if "token_distribution" in result.metadata
                else 0,
            )
            chunk_objects.append(chunk)
            self.db.add(chunk)

        # Update document
        document.is_processed = True
        await self.db.flush()

        logger.debug(f"Created {len(chunk_objects)} chunks for document {document.id}")
        return len(chunk_objects)

    async def reprocess_document(
        self,
        document_id: str,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
        strategy: str = "semantic",
    ) -> int:
        """
        Reprocess a document (delete old chunks and create new ones)

        Args:
            document_id: ID of document to reprocess
            chunk_size: Target chunk size
            chunk_overlap: Overlap between chunks
            strategy: Chunking strategy

        Returns:
            Number of chunks created
        """
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Delete existing chunks
        await self.db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
        )
        existing_chunks = (
            (await self.db.execute(
                select(DocumentChunk).where(DocumentChunk.document_id == document_id)
            ))
            .scalars()
            .all()
        )

        for chunk in existing_chunks:
            await self.db.delete(chunk)

        # Reset processing flag
        document.is_processed = False

        # Reprocess
        chunks_created = await self._process_document(
            document,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
        )

        await self.db.commit()
        return chunks_created

    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about document processing"""
        # Count total documents
        result = await self.db.execute(select(Document))
        total_docs = len(result.scalars().all())

        # Count processed
        result = await self.db.execute(
            select(Document).where(Document.is_processed == True)
        )
        processed_docs = len(result.scalars().all())

        # Count chunks
        result = await self.db.execute(select(DocumentChunk))
        total_chunks = len(result.scalars().all())

        # Calculate average chunk size
        result = await self.db.execute(select(DocumentChunk.token_count))
        token_counts = result.scalars().all()
        avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0

        return {
            "total_documents": total_docs,
            "processed_documents": processed_docs,
            "unprocessed_documents": total_docs - processed_docs,
            "total_chunks": total_chunks,
            "avg_chunk_tokens": avg_tokens,
            "processing_rate": f"{(processed_docs / total_docs * 100):.1f}%"
            if total_docs > 0
            else "0%",
        }
