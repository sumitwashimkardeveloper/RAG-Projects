import pytest
from unittest.mock import Mock, MagicMock
from modules.retriever import Retriever, Document, RetrievalResult

@pytest.fixture
def mock_db_manager():
    db_manager = Mock()
    db_manager.get_vector_store = Mock(return_value=None)
    return db_manager

@pytest.fixture
def retriever(mock_db_manager):
    return Retriever(config=None, db_manager=mock_db_manager)

@pytest.fixture
def sample_search_results():
    return [
        {"id": "doc1", "score": 0.95, "metadata": {"content": "Python is great", "source": "python.org"}},
        {"id": "doc2", "score": 0.85, "metadata": {"content": "Python data science", "source": "ml.org"}},
    ]

def test_retriever_initialization(retriever):
    assert retriever.logger is not None
    assert retriever.semantic_searcher is not None or retriever.keyword_searcher is not None
    assert retriever.ranking_engine is not None
    assert retriever.filter_pipeline is not None

def test_document_dataclass():
    doc = Document(
        content="Test content",
        source="test.txt",
        metadata={"key": "value"},
        relevance_score=0.9,
        rank=1
    )

    assert doc.content == "Test content"
    assert doc.relevance_score == 0.9
    assert doc.rank == 1

def test_retrieval_result_dataclass():
    docs = [Document("content", "source")]
    result = RetrievalResult(
        query="test query",
        documents=docs,
        total_retrieved=1,
        search_strategy="hybrid"
    )

    assert result.query == "test query"
    assert len(result.documents) == 1
    assert result.search_strategy == "hybrid"

def test_rank_results(retriever, sample_search_results):
    ranked = retriever.rank_results(sample_search_results)

    assert all("rank" in r for r in ranked)
    assert ranked[0]["rank"] == 1

def test_deduplicate(retriever):
    results = [
        {"id": "doc1", "score": 0.9},
        {"id": "doc1", "score": 0.8},
        {"id": "doc2", "score": 0.7}
    ]

    deduplicated = retriever.deduplicate(results)

    assert len(deduplicated) == 2

def test_filter_results(retriever, sample_search_results):
    filtered = retriever.filter_results(sample_search_results, score_threshold=0.9)

    assert all(r.get("score", 0) >= 0.9 for r in filtered)

def test_convert_to_documents(retriever, sample_search_results):
    documents = retriever._convert_to_documents(sample_search_results)

    assert isinstance(documents, list)
    assert all(isinstance(d, Document) for d in documents)
    assert documents[0].rank == 1

def test_set_retrieval_config(retriever):
    retriever.set_retrieval_config(top_k=10, score_threshold=0.5)

def test_semantic_search_not_initialized():
    db_manager = Mock()
    db_manager.get_vector_store = Mock(return_value=None)
    retriever = Retriever(config=None, db_manager=db_manager)

    retriever.semantic_searcher = None
    results = retriever.semantic_search("test query")

    assert results == []

def test_keyword_search_not_initialized():
    db_manager = Mock()
    db_manager.get_vector_store = Mock(return_value=None)
    retriever = Retriever(config=None, db_manager=db_manager)

    retriever.keyword_searcher = None
    results = retriever.keyword_search("test query")

    assert results == []
