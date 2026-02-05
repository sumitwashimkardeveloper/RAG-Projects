import pytest
from modules.retriever import KeywordSearch, BM25

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "content": "Python is a programming language for data science",
            "metadata": {"source": "python.org"}
        },
        {
            "id": "doc2",
            "content": "JavaScript is used for web development",
            "metadata": {"source": "javascript.info"}
        },
        {
            "id": "doc3",
            "content": "Machine learning with Python and data analysis",
            "metadata": {"source": "ml.org"}
        }
    ]

@pytest.fixture
def bm25_index(sample_documents):
    return BM25(sample_documents)

@pytest.fixture
def keyword_search(sample_documents):
    ks = KeywordSearch()
    ks.build_index(sample_documents)
    return ks

def test_bm25_initialization(bm25_index, sample_documents):
    assert bm25_index.avgdl > 0
    assert len(bm25_index.idf) > 0
    assert len(bm25_index.doc_vectors) == len(sample_documents)

def test_bm25_search(bm25_index):
    results = bm25_index.search("Python data", top_k=2)

    assert len(results) <= 2
    assert all("score" in r for r in results)

def test_keyword_search_basic(keyword_search):
    results = keyword_search.search("Python programming", top_k=3)

    assert len(results) <= 3
    assert all("score" in r for r in results)

def test_keyword_search_by_keywords(keyword_search):
    results = keyword_search.search_by_keywords(["Python", "data"], top_k=2)

    assert len(results) <= 2

def test_keyword_search_with_threshold(keyword_search):
    results = keyword_search.search("Python", top_k=5, score_threshold=0.1)

    assert all(r.get("score", 0) >= 0.1 for r in results)

def test_keyword_search_with_filters(keyword_search):
    filters = {"source": "python.org"}
    results = keyword_search.search_with_filters("Python", metadata_filters=filters, top_k=5)

    for result in results:
        assert result.get("metadata", {}).get("source") == "python.org"

def test_tokenization(bm25_index):
    tokens = bm25_index._tokenize("Hello, World! This is a test.")

    assert "hello" in tokens
    assert "world" in tokens
    assert "," not in tokens
