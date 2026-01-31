from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4-turbo-preview"

    chunk_size: int = 1024
    chunk_overlap: int = 256

    top_k_entities: int = 10
    top_k_paths: int = 5

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"

settings = Settings()
