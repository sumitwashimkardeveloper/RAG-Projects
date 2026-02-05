import pytest
from modules.critic import ConfidenceScorer

@pytest.fixture
def scorer():
    return ConfidenceScorer()

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "score": 0.95,
            "relevance_score": 0.9,
            "metadata": {
                "source": "arxiv.org",
                "content": "High quality content about machine learning",
                "timestamp": "2024-01-01T00:00:00"
            }
        },
        {
            "id": "doc2",
            "score": 0.7,
            "relevance_score": 0.7,
            "metadata": {
                "source": "blog.com",
                "content": "Some content",
                "timestamp": "2023-01-01T00:00:00"
            }
        }
    ]

def test_score_basic(scorer, sample_documents):
    confidence = scorer.score(sample_documents)

    assert 0 <= confidence <= 1

def test_score_empty_documents(scorer):
    confidence = scorer.score([])

    assert confidence == 0.0

def test_source_confidence_arxiv(scorer):
    document = {
        "metadata": {"source": "arxiv.org paper"}
    }

    confidence = scorer._source_confidence(document)

    assert confidence > 0.9

def test_source_confidence_unknown(scorer):
    document = {
        "metadata": {"source": "unknown.com"}
    }

    confidence = scorer._source_confidence(document)

    assert confidence < 0.5

def test_recency_recent(scorer):
    from datetime import datetime, timedelta

    recent_date = (datetime.now() - timedelta(days=10)).isoformat()
    document = {
        "metadata": {"timestamp": recent_date}
    }

    score = scorer._recency_score(document)

    assert score > 0.8

def test_recency_old(scorer):
    from datetime import datetime, timedelta

    old_date = (datetime.now() - timedelta(days=500)).isoformat()
    document = {
        "metadata": {"timestamp": old_date}
    }

    score = scorer._recency_score(document)

    assert score < 0.5

def test_score_distribution(scorer, sample_documents):
    distribution = scorer.score_distribution(sample_documents)

    assert "mean" in distribution
    assert "min" in distribution
    assert "max" in distribution
    assert "std_dev" in distribution

def test_is_confident_high(scorer, sample_documents):
    confident = scorer.is_confident(sample_documents, threshold=0.3)

    assert isinstance(confident, bool)

def test_is_confident_low(scorer, sample_documents):
    confident = scorer.is_confident(sample_documents, threshold=0.99)

    assert confident == False
