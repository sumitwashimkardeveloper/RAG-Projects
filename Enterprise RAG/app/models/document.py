"""
Document and Ingestion Models
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
import uuid
import enum

from app.database import Base


class DocumentSource(str, enum.Enum):
    """Enum for document sources"""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"
    CONFLUENCE = "confluence"
    NOTION = "notion"
    SHAREPOINT = "sharepoint"
    GOOGLE_DRIVE = "google_drive"
    EMAIL = "email"
    WEBSITE = "website"
    MARKDOWN = "markdown"
    PLAINTEXT = "plaintext"


class SyncStatus(str, enum.Enum):
    """Enum for sync status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class DataSource(Base):
    """
    Represents a data source connection
    (Confluence workspace, Notion database, SharePoint site, etc.)
    """
    __tablename__ = "data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # confluence, notion, sharepoint, etc.
    is_active = Column(Boolean, default=True, index=True)

    # Connection details (encrypted in production)
    config = Column(JSONB, nullable=False)  # API keys, URLs, credentials

    # Sync information
    last_synced_at = Column(DateTime, nullable=True)
    next_sync_at = Column(DateTime, nullable=True)
    sync_interval_hours = Column(Integer, default=24)
    sync_status = Column(String(20), default=SyncStatus.PENDING.value)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="data_source", cascade="all, delete-orphan")
    sync_logs = relationship("SyncLog", back_populates="data_source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DataSource(id={self.id}, name={self.name}, type={self.type})>"


class Document(Base):
    """
    Represents a document ingested from any source
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Document identification
    external_id = Column(String(500), nullable=True)  # ID from source system
    title = Column(String(500), nullable=False, index=True)

    # Content
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=True, unique=True)  # For dedup

    # Source information
    source_type = Column(String(50), nullable=False)  # pdf, confluence, notion, etc.
    source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=True)
    source_url = Column(String(2000), nullable=True)

    # Document metadata
    author = Column(String(255), nullable=True)
    document_type = Column(String(100), nullable=True)
    file_path = Column(String(1000), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_created_at = Column(DateTime, nullable=True)
    source_updated_at = Column(DateTime, nullable=True)

    # Processing status
    is_processed = Column(Boolean, default=False, index=True)
    is_embedded = Column(Boolean, default=False, index=True)
    processing_error = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSONB, nullable=True)  # Custom metadata from source
    tags = Column(ARRAY(String), nullable=True)
    language = Column(String(10), nullable=True, default="en")

    # Relationships
    data_source = relationship("DataSource", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        # Index for efficient filtering
        ('source_type', 'is_processed', 'is_embedded'),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, source_type={self.source_type})>"


class DocumentChunk(Base):
    """
    Represents a chunk of a document (for embedding and retrieval)
    """
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Reference to parent document
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True)

    # Chunk content
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order within document

    # Chunk metadata
    token_count = Column(Integer, nullable=True)
    embedding_id = Column(String(500), nullable=True)  # ID in vector DB

    # Processing status
    is_embedded = Column(Boolean, default=False, index=True)
    embedding_error = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    embedded_at = Column(DateTime, nullable=True)

    # Relationship
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>"


class SyncLog(Base):
    """
    Audit log for data source synchronizations
    """
    __tablename__ = "sync_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Reference to data source
    data_source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id"), nullable=False, index=True)

    # Sync details
    status = Column(String(20), nullable=False)  # pending, in_progress, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Results
    documents_processed = Column(Integer, default=0)
    documents_created = Column(Integer, default=0)
    documents_updated = Column(Integer, default=0)
    documents_failed = Column(Integer, default=0)

    # Error information
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, nullable=True)

    # Relationship
    data_source = relationship("DataSource", back_populates="sync_logs")

    def __repr__(self):
        return f"<SyncLog(id={self.id}, source_id={self.data_source_id}, status={self.status})>"


class IngestionMetrics(Base):
    """
    Track ingestion performance metrics
    """
    __tablename__ = "ingestion_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metrics
    total_documents = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    total_embedded = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)

    # Performance
    avg_processing_time = Column(Float, nullable=True)  # seconds per document
    avg_chunk_size = Column(Integer, nullable=True)  # tokens

    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<IngestionMetrics(total_docs={self.total_documents}, total_chunks={self.total_chunks})>"
