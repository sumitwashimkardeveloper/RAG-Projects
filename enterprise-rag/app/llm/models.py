from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid

from app.database import Base


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class QueryResponse(Base):
    __tablename__ = "query_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    model = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)

    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)

    retrieved_chunks = Column(Integer, default=0)
    sources = Column(JSONB, nullable=True)

    confidence_score = Column(Float, nullable=True)
    has_citation = Column(Boolean, default=False)

    user_feedback = Column(String(20), nullable=True)
    user_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    metadata = Column(JSONB, nullable=True)


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    template = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=True)

    variables = Column(JSONB, nullable=False)
    version = Column(Integer, default=1)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResponseFeedback(Base):
    __tablename__ = "response_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = Column(UUID(as_uuid=True), ForeignKey("query_responses.id"), nullable=False, index=True)

    rating = Column(Integer, nullable=True)
    helpful = Column(Boolean, nullable=True)
    accurate = Column(Boolean, nullable=True)
    complete = Column(Boolean, nullable=True)

    comments = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    query_response = relationship("QueryResponse")
