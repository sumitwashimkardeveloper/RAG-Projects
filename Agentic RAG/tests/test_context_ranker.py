import pytest
from modules.answer_generator import ContextRanker

@pytest.fixture
def ranker():
    return ContextRanker()

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "score": 0.9,
            "metadata": {
                "content": "Python is a powerful programming language used for data science and machine learning. It has excellent libraries.",
                "source": "python.org"
            }
        },
        {
            "id": "doc2",
            "score": 0.5,
            "metadata": {
                "content": "Short",
                "source": "blog.com"
            }
        },
        {
            "id": "doc3",
            "score": 0.8,
            "metadata": {
                "content": "Machine learning algorithms can be implemented in Python using libraries like scikit-learn and TensorFlow.",
                "source": "arxiv.org"
            }
        }
    ]

def test_rank_documents(ranker, sample_documents):
    query = "Python machine learning"
    ranked = ranker.rank_documents(query, sample_documents)

    assert len(ranked) == len(sample_documents)
    assert "context_score" in ranked[0]

def test_score_document_length(ranker):
    short = "brief"
    medium = " ".join(["word"] * 100)
    long = " ".join(["word"] * 600)

    score_short = ranker._score_document_length(short)
    score_medium = ranker._score_document_length(medium)
    score_long = ranker._score_document_length(long)

    assert score_short < score_medium
    assert score_medium > score_long or score_long >= 0.5

def test_score_keyword_match(ranker):
    query = "Python machine learning"
    matching = "Python is used for machine learning"
    not_matching = "Java is used for backend"

    score_matching = ranker._score_keyword_match(query, matching)
    score_not = ranker._score_keyword_match(query, not_matching)

    assert score_matching > score_not

def test_select_top_k(ranker, sample_documents):
    query = "Python"
    top = ranker.select_top_k(query, sample_documents, k=2)

    assert len(top) == 2

def test_filter_by_threshold(ranker, sample_documents):
    query = "Python"
    filtered = ranker.filter_by_threshold(query, sample_documents, threshold=0.5)

    assert len(filtered) > 0
    assert all(doc.get("context_score", 0) >= 0.5 for doc in filtered)
