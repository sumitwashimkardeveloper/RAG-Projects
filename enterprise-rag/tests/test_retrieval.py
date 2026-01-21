import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.retrieval.hybrid import HybridRetriever


class TestHybridRetriever:

    @pytest.mark.asyncio
    async def test_combine_results(self):
        db_mock = AsyncMock()
        embedding_service_mock = AsyncMock()

        retriever = HybridRetriever(db_mock, embedding_service_mock)

        vector_results = [
            {"chunk_id": "1", "document_id": "d1", "content": "text1", "score": 0.9, "source": "vector"},
            {"chunk_id": "2", "document_id": "d2", "content": "text2", "score": 0.8, "source": "vector"},
        ]

        keyword_results = [
            {"chunk_id": "1", "document_id": "d1", "content": "text1", "score": 0.7, "source": "keyword"},
            {"chunk_id": "3", "document_id": "d3", "content": "text3", "score": 0.6, "source": "keyword"},
        ]

        combined = retriever._combine_results(vector_results, keyword_results)

        assert len(combined) == 3
        assert combined[0]["chunk_id"] in ["1", "2", "3"]
        assert all("score" in result for result in combined)

    def test_combine_results_with_weights(self):
        db_mock = Mock()
        embedding_service_mock = Mock()
        retriever = HybridRetriever(db_mock, embedding_service_mock)

        vector_results = [
            {"chunk_id": "1", "document_id": "d1", "content": "text", "score": 1.0, "source": "vector"},
        ]

        keyword_results = [
            {"chunk_id": "1", "document_id": "d1", "content": "text", "score": 1.0, "source": "keyword"},
        ]

        combined = retriever._combine_results(
            vector_results,
            keyword_results,
            vector_weight=0.8,
            keyword_weight=0.2
        )

        expected_score = (1.0 * 0.8) + (1.0 * 0.2)
        assert combined[0]["score"] == expected_score

    def test_combine_results_single_source(self):
        db_mock = Mock()
        embedding_service_mock = Mock()
        retriever = HybridRetriever(db_mock, embedding_service_mock)

        vector_results = [
            {"chunk_id": "1", "document_id": "d1", "content": "text", "score": 0.9, "source": "vector"},
        ]

        combined = retriever._combine_results(vector_results, [])

        assert len(combined) == 1
        assert combined[0]["chunk_id"] == "1"
        assert "vector" in combined[0]["sources"]
        assert "keyword" not in combined[0]["sources"]
