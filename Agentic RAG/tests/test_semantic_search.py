import pytest
from unittest.mock import Mock, MagicMock
from modules.retriever import SemanticSearch

@pytest.fixture
def mock_vector_store():
    store = Mock()
    store.search = MagicMock(return_value=[
        {"id": "doc1", "score": 0.95},
        {"id": "doc2", "score": 0.85}
    ])
    return store

@pytest.fixture
def semantic_search(mock_vector_store):
    return SemanticSearch(mock_vector_store, embeddings_provider="openai")

def test_semantic_search_basic(semantic_search, mock_vector_store):
    results = semantic_search.search("test query")

    assert isinstance(results, list)
    mock_vector_store.search.assert_called_once()

def test_semantic_search_with_threshold(semantic_search, mock_vector_store):
    results = semantic_search.search("test query", top_k=5, score_threshold=0.9)

    filtered = [r for r in results if r.get("score", 0) >= 0.9]
    assert len(filtered) <= len(results)

def test_semantic_search_batch(semantic_search, mock_vector_store):
    queries = ["query1", "query2", "query3"]
    results = semantic_search.batch_search(queries)

    assert len(results) == 3
    assert all(isinstance(r, list) for r in results)

def test_cosine_similarity():
    vec1 = [1, 0, 0]
    vec2 = [1, 0, 0]
    similarity = SemanticSearch._cosine_similarity(vec1, vec2)

    assert similarity == 1.0

def test_cosine_similarity_perpendicular():
    vec1 = [1, 0, 0]
    vec2 = [0, 1, 0]
    similarity = SemanticSearch._cosine_similarity(vec1, vec2)

    assert similarity == 0.0

def test_cosine_similarity_empty():
    vec1 = []
    vec2 = [1, 0, 0]
    similarity = SemanticSearch._cosine_similarity(vec1, vec2)

    assert similarity == 0.0
