"""
Database Configuration and Connection Management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base for ORM models
Base = declarative_base()

# Import models to register them with Base
from app.models import DataSource, Document, DocumentChunk, SyncLog, IngestionMetrics
from app.embeddings.models import Embedding, EmbeddingCache
from app.llm.models import QueryResponse, PromptTemplate, ResponseFeedback

# Async engine instance
engine = None
async_session_maker = None


async def init_db():
    """
    Initialize database connection pool and create tables
    """
    global engine, async_session_maker

    try:
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

        # Create session factory
        async_session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


async def close_db():
    """
    Close database connection pool
    """
    global engine

    if engine:
        await engine.dispose()
        logger.info("Database connection closed")


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session
    """
    if not async_session_maker:
        raise RuntimeError("Database not initialized")

    async with async_session_maker() as session:
        yield session
