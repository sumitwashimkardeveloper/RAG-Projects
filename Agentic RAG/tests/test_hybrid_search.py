import pytest
from unittest.mock import Mock
from modules.retriever import HybridSearch

@pytest.fixture
def mock_semantic_searcher():
    searcher = Mock()
    searcher.search = Mock(return_value=[
        {"id": "doc1", "score": 0.95, "metadata": {}},
        {"id": "doc2", "score": 0.85, "metadata": {}}
    ])
    return searcher

@pytest.fixture
def mock_keyword_searcher():
    searcher = Mock()
    searcher.search = Mock(return_value=[
        {"id": "doc1", "score": 50, "metadata": {}},
        {"id": "doc3", "score": 40, "metadata": {}}
    ])
    return searcher

@pytest.fixture
def hybrid_search(mock_semantic_searcher, mock_keyword_searcher):
    return HybridSearch(
        semantic_searcher=mock_semantic_searcher,
        keyword_searcher=mock_keyword_searcher,
        semantic_weight=0.7,
        keyword_weight=0.3
    )

def test_hybrid_search_combines_results(hybrid_search):
    results = hybrid_search.search("test query", top_k=5)

    assert isinstance(results, list)
    doc_ids = {r["id"] for r in results}
    assert "doc1" in doc_ids

def test_hybrid_search_with_threshold(hybrid_search):
    results = hybrid_search.search("test query", top_k=5, score_threshold=0.3)

    assert all(r.get("score", 0) >= 0.3 for r in results)

def test_hybrid_search_strategy_semantic(hybrid_search):
    results = hybrid_search.search_with_strategy("test query", strategy="semantic", top_k=5)

    assert len(results) > 0

def test_hybrid_search_strategy_keyword(hybrid_search):
    results = hybrid_search.search_with_strategy("test query", strategy="keyword", top_k=5)

    assert len(results) > 0

def test_hybrid_search_strategy_hybrid(hybrid_search):
    results = hybrid_search.search_with_strategy("test query", strategy="hybrid", top_k=5)

    assert len(results) > 0

def test_adjust_weights(hybrid_search):
    hybrid_search.adjust_weights(0.6, 0.4)

    assert hybrid_search.semantic_weight == 0.6
    assert hybrid_search.keyword_weight == 0.4

def test_weight_normalization(hybrid_search):
    hybrid_search.adjust_weights(0.8, 0.4)

    total_weight = hybrid_search.semantic_weight + hybrid_search.keyword_weight
    assert abs(total_weight - 1.0) < 0.01

def test_no_semantic_searcher():
    keyword_searcher = Mock()
    keyword_searcher.search = Mock(return_value=[{"id": "doc1", "score": 50}])

    hybrid = HybridSearch(semantic_searcher=None, keyword_searcher=keyword_searcher)
    results = hybrid.search("test query")

    assert len(results) > 0
