import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.llm.base import BaseLLMProvider
from app.llm.prompts import PromptService


class MockLLMProvider(BaseLLMProvider):
    def generate(self, messages, temperature=None, max_tokens=None):
        return "Test response"

    async def generate_async(self, messages, temperature=None, max_tokens=None):
        return "Test response"

    async def stream(self, messages, temperature=None, max_tokens=None):
        yield "Test "
        yield "response"


class TestLLMProvider:

    def test_format_messages_with_context(self):
        provider = MockLLMProvider("test-model")

        messages = provider.format_messages(
            system_prompt="You are helpful",
            user_query="What is this?",
            context=["Context 1", "Context 2"]
        )

        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert "Context 1" in messages[-1]["content"]

    def test_format_messages_without_context(self):
        provider = MockLLMProvider("test-model")

        messages = provider.format_messages(
            system_prompt="You are helpful",
            user_query="What is this?"
        )

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "What is this?"

    def test_estimate_tokens(self):
        provider = MockLLMProvider("test-model")
        text = "This is a test sentence"
        tokens = provider.estimate_tokens(text)
        assert tokens > 0

    @pytest.mark.asyncio
    async def test_generate_async(self):
        provider = MockLLMProvider("test-model")
        messages = [{"role": "user", "content": "Hello"}]
        response = await provider.generate_async(messages)
        assert response == "Test response"

    def test_generate_sync(self):
        provider = MockLLMProvider("test-model")
        messages = [{"role": "user", "content": "Hello"}]
        response = provider.generate(messages)
        assert response == "Test response"

    @pytest.mark.asyncio
    async def test_stream(self):
        provider = MockLLMProvider("test-model")
        messages = [{"role": "user", "content": "Hello"}]
        chunks = []
        async for chunk in provider.stream(messages):
            chunks.append(chunk)
        assert len(chunks) > 0
        assert "".join(chunks) == "Test response"


class TestPromptService:

    def test_format_rag_prompt(self):
        prompt = PromptService.format_rag_prompt(
            question="What is RAG?",
            context=["Context 1", "Context 2"]
        )

        assert "system" in prompt
        assert "user" in prompt or any("what" in str(v).lower() for v in prompt.values())

    def test_add_citations(self):
        response = "This is the answer"
        sources = [
            {"title": "Document 1", "url": "http://example.com/1"},
            {"title": "Document 2", "url": "http://example.com/2"}
        ]

        result = PromptService.add_citations(response, sources)

        assert "Document 1" in result
        assert "Document 2" in result
        assert "Sources:" in result

    def test_add_citations_no_sources(self):
        response = "This is the answer"
        result = PromptService.add_citations(response, [])
        assert result == response

    def test_extract_answer_from_response(self):
        response = """Here is the answer:

The answer is yes.

Sources:
1. Document 1"""

        answer = PromptService.extract_answer_from_response(response)
        assert "yes" in answer.lower()
        assert "source" not in answer.lower()

    def test_format_with_context(self):
        template = "Question: {question}\nContext: {context}"
        result = PromptService.format_with_context(
            template,
            context="Some context",
            question="What?"
        )

        assert "What?" in result
        assert "Some context" in result
