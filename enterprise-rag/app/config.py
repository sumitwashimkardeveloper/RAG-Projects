"""
Application Configuration Settings
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application Configuration
    APP_NAME: str = Field(default="Enterprise Knowledge RAG", env="APP_NAME")
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # API Server
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=4, env="API_WORKERS")
    API_RELOAD: bool = Field(default=True, env="API_RELOAD")

    # Security
    SECRET_KEY: str = Field(default="change-me-in-production", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )

    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://rag_user:rag_password@localhost:5432/enterprise_rag",
        env="DATABASE_URL"
    )
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")

    # Redis Configuration
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: str = Field(default="", env="REDIS_PASSWORD")

    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Vector Database - Pinecone
    PINECONE_API_KEY: str = Field(default="", env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = Field(default="us-east-1-aws", env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = Field(default="enterprise-rag", env="PINECONE_INDEX_NAME")
    PINECONE_NAMESPACE: str = Field(default="default", env="PINECONE_NAMESPACE")

    # Vector Database - Weaviate
    WEAVIATE_URL: str = Field(default="http://localhost:8080", env="WEAVIATE_URL")
    WEAVIATE_API_KEY: str = Field(default="", env="WEAVIATE_API_KEY")

    # Embedding Configuration
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    EMBEDDING_BATCH_SIZE: int = Field(default=100, env="EMBEDDING_BATCH_SIZE")
    EMBEDDING_DIMENSION: int = Field(default=1536, env="EMBEDDING_DIMENSION")

    # LLM Configuration - OpenAI
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    OPENAI_MAX_TOKENS: int = Field(default=2048, env="OPENAI_MAX_TOKENS")

    # LLM Configuration - Anthropic
    ANTHROPIC_API_KEY: str = Field(default="", env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field(default="claude-3-opus-20240229", env="ANTHROPIC_MODEL")

    # LLM Configuration - Local
    LOCAL_LLM_ENDPOINT: str = Field(default="http://localhost:11434", env="LOCAL_LLM_ENDPOINT")
    LOCAL_LLM_MODEL: str = Field(default="mistral", env="LOCAL_LLM_MODEL")
    USE_LOCAL_LLM: bool = Field(default=False, env="USE_LOCAL_LLM")

    # Confluence Configuration
    CONFLUENCE_URL: str = Field(default="", env="CONFLUENCE_URL")
    CONFLUENCE_USERNAME: str = Field(default="", env="CONFLUENCE_USERNAME")
    CONFLUENCE_API_TOKEN: str = Field(default="", env="CONFLUENCE_API_TOKEN")
    CONFLUENCE_SPACES: List[str] = Field(default=[], env="CONFLUENCE_SPACES")
    CONFLUENCE_SYNC_INTERVAL_HOURS: int = Field(default=24, env="CONFLUENCE_SYNC_INTERVAL_HOURS")

    # Notion Configuration
    NOTION_API_KEY: str = Field(default="", env="NOTION_API_KEY")
    NOTION_DATABASE_IDS: List[str] = Field(default=[], env="NOTION_DATABASE_IDS")
    NOTION_SYNC_INTERVAL_HOURS: int = Field(default=24, env="NOTION_SYNC_INTERVAL_HOURS")

    # SharePoint Configuration
    SHAREPOINT_TENANT_ID: str = Field(default="", env="SHAREPOINT_TENANT_ID")
    SHAREPOINT_CLIENT_ID: str = Field(default="", env="SHAREPOINT_CLIENT_ID")
    SHAREPOINT_CLIENT_SECRET: str = Field(default="", env="SHAREPOINT_CLIENT_SECRET")
    SHAREPOINT_SITES: List[str] = Field(default=[], env="SHAREPOINT_SITES")
    SHAREPOINT_SYNC_INTERVAL_HOURS: int = Field(default=24, env="SHAREPOINT_SYNC_INTERVAL_HOURS")

    # Google Configuration
    GOOGLE_APPLICATION_CREDENTIALS: str = Field(default="", env="GOOGLE_APPLICATION_CREDENTIALS")
    GOOGLE_FOLDER_IDS: List[str] = Field(default=[], env="GOOGLE_FOLDER_IDS")
    GOOGLE_SYNC_INTERVAL_HOURS: int = Field(default=24, env="GOOGLE_SYNC_INTERVAL_HOURS")

    # Email Configuration
    EMAIL_IMAP_SERVER: str = Field(default="imap.gmail.com", env="EMAIL_IMAP_SERVER")
    EMAIL_IMAP_PORT: int = Field(default=993, env="EMAIL_IMAP_PORT")
    EMAIL_USERNAME: str = Field(default="", env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field(default="", env="EMAIL_PASSWORD")
    EMAIL_SYNC_INTERVAL_HOURS: int = Field(default=24, env="EMAIL_SYNC_INTERVAL_HOURS")

    # Celery Configuration
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND")
    CELERY_TASK_SERIALIZER: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    CELERY_TIMEZONE: str = Field(default="UTC", env="CELERY_TIMEZONE")

    # Monitoring
    SENTRY_DSN: str = Field(default="", env="SENTRY_DSN")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    ENABLE_PROMETHEUS_METRICS: bool = Field(default=True, env="ENABLE_PROMETHEUS_METRICS")
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")

    # Retrieval Configuration
    MAX_RETRIEVED_DOCUMENTS: int = Field(default=10, env="MAX_RETRIEVED_DOCUMENTS")
    CHUNK_SIZE: int = Field(default=1024, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")
    SIMILARITY_THRESHOLD: float = Field(default=0.5, env="SIMILARITY_THRESHOLD")
    ENABLE_RERANKING: bool = Field(default=True, env="ENABLE_RERANKING")
    RERANKER_MODEL: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-12-v2",
        env="RERANKER_MODEL"
    )

    # Document Processing
    MAX_DOCUMENT_SIZE_MB: int = Field(default=50, env="MAX_DOCUMENT_SIZE_MB")
    SUPPORTED_FILE_TYPES: List[str] = Field(
        default=["pdf", "docx", "xlsx", "csv", "txt", "md", "pptx"],
        env="SUPPORTED_FILE_TYPES"
    )
    ENABLE_OCR: bool = Field(default=False, env="ENABLE_OCR")

    # Caching
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    QUERY_RESULT_CACHE_TTL: int = Field(default=1800, env="QUERY_RESULT_CACHE_TTL")
    EMBEDDING_CACHE_ENABLED: bool = Field(default=True, env="EMBEDDING_CACHE_ENABLED")

    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    RATE_LIMIT_REQUESTS_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_REQUESTS_PER_HOUR")

    # Admin Configuration
    ADMIN_EMAIL: str = Field(default="admin@company.com", env="ADMIN_EMAIL")
    ENABLE_ADMIN_PANEL: bool = Field(default=True, env="ENABLE_ADMIN_PANEL")

    # Feature Flags
    ENABLE_STREAMING_RESPONSES: bool = Field(default=True, env="ENABLE_STREAMING_RESPONSES")
    ENABLE_FEEDBACK_COLLECTION: bool = Field(default=True, env="ENABLE_FEEDBACK_COLLECTION")
    ENABLE_USAGE_TRACKING: bool = Field(default=True, env="ENABLE_USAGE_TRACKING")
    ENABLE_COST_TRACKING: bool = Field(default=True, env="ENABLE_COST_TRACKING")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
