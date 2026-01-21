import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.processing import TextProcessor
from app.llm.base import BaseLLMProvider
from app.llm.prompts import PromptService


class MockEmbeddingProvider(BaseLLMProvider):
    def generate(self, messages, temperature=None, max_tokens=None):
        return "Generated response based on context"

    async def generate_async(self, messages, temperature=None, max_tokens=None):
        return "Generated response based on context"

    async def stream(self, messages, temperature=None, max_tokens=None):
        response = "Generated response based on context"
        for char in response:
            yield char


class TestFullRAGPipeline:

    def test_document_processing_pipeline(self):
        raw_text = """
        Introduction to RAG

        RAG (Retrieval Augmented Generation) is a technique for combining
        retrieval and generation models. It works by first retrieving relevant
        documents and then generating a response based on those documents.

        Key Components

        1. Retrieval: Finding relevant documents
        2. Augmentation: Adding context to queries
        3. Generation: Creating responses from context
        """

        processor = TextProcessor(chunk_size=200, chunk_overlap=50)
        result = processor.process(raw_text, strategy="semantic")

        assert len(result.chunks) > 0
        assert result.metadata["num_chunks"] > 0
        assert result.metadata["compression_ratio"] > 0

    def test_prompt_formatting_pipeline(self):
        question = "What is RAG?"
        context = [
            "RAG is Retrieval Augmented Generation",
            "It combines retrieval and generation",
            "Used for question answering"
        ]

        prompt = PromptService.format_rag_prompt(question, context)

        assert "system" in prompt
        assert "RAG" in prompt.get("system", "") or "RAG" in prompt.get("user", "")

    @pytest.mark.asyncio
    async def test_end_to_end_qa_pipeline(self):
        raw_documents = [
            "Document 1: Machine learning is a subset of AI",
            "Document 2: Deep learning uses neural networks",
            "Document 3: NLP processes text data"
        ]

        processor = TextProcessor(chunk_size=100)
        all_chunks = []

        for doc in raw_documents:
            result = processor.process(doc)
            all_chunks.extend(result.chunks)

        assert len(all_chunks) > 0

        question = "What is machine learning?"
        context = [chunk for chunk in all_chunks if "machine" in chunk.lower() or "AI" in chunk]

        llm = MockEmbeddingProvider("test-model")
        messages = llm.format_messages(
            system_prompt="You are helpful",
            user_query=question,
            context=context
        )

        response = await llm.generate_async(messages)
        assert response is not None
        assert len(response) > 0

    def test_response_with_citations(self):
        response = "Machine learning is a subset of AI"
        sources = [
            {"title": "AI Basics", "url": "https://example.com/ai"},
            {"title": "ML Guide", "url": "https://example.com/ml"}
        ]

        cited_response = PromptService.add_citations(response, sources)

        assert "Machine learning" in cited_response
        assert "AI Basics" in cited_response
        assert "ML Guide" in cited_response
        assert "Sources:" in cited_response

    @pytest.mark.asyncio
    async def test_streaming_response(self):
        llm = MockEmbeddingProvider("test-model")
        messages = [{"role": "user", "content": "Hello"}]

        chunks = []
        async for chunk in llm.stream(messages):
            chunks.append(chunk)

        full_response = "".join(chunks)
        assert len(full_response) > 0
        assert "Generated" in full_response

    def test_chunking_strategies(self):
        text = """
        # Main Topic

        Introduction paragraph.

        ## Subtopic 1

        Content for subtopic 1.
        More details here.

        ## Subtopic 2

        Content for subtopic 2.
        Additional information.
        """

        processor = TextProcessor(chunk_size=150)

        semantic_chunks = processor.process(text, strategy="semantic").chunks
        sentence_chunks = processor.process(text, strategy="sentence").chunks
        heading_chunks = processor.process(text, strategy="heading").chunks

        assert len(semantic_chunks) > 0
        assert len(sentence_chunks) > 0
        assert len(heading_chunks) > 0
