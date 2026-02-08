import pytest
from modules.answer_generator import CitationTracker

@pytest.fixture
def tracker():
    return CitationTracker()

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "metadata": {
                "content": "Python is a programming language. It was created in 1991.",
                "source": "python.org"
            }
        },
        {
            "id": "doc2",
            "metadata": {
                "content": "Machine learning uses algorithms to learn from data.",
                "source": "ml.org"
            }
        }
    ]

def test_extract_citations(tracker, sample_documents):
    answer = "Python is a programming language used for machine learning with many algorithms."
    citations = tracker.extract_citations(answer, sample_documents)

    assert len(citations) > 0
    assert all(hasattr(c, 'source') for c in citations)

def test_create_citation_list(tracker, sample_documents):
    answer = "Python is a programming language"
    citations = tracker.extract_citations(answer, sample_documents)
    citation_list = tracker.create_citation_list(citations)

    assert len(citation_list) > 0
    assert all("source" in c for c in citation_list)

def test_format_citations_markdown(tracker, sample_documents):
    answer = "Python is great for machine learning"
    citations = tracker.extract_citations(answer, sample_documents)
    markdown = tracker.format_citations_markdown(citations)

    assert "## Sources" in markdown or markdown == ""

def test_validate_citations(tracker, sample_documents):
    answer = "Python and machine learning"
    citations = tracker.extract_citations(answer, sample_documents)
    validation = tracker.validate_citations(citations)

    assert "total_citations" in validation
    assert "unique_sources" in validation
    assert "average_relevance" in validation

def test_get_top_citations(tracker, sample_documents):
    answer = "Python is used for machine learning with various algorithms"
    citations = tracker.extract_citations(answer, sample_documents)
    top = tracker.get_top_citations(k=2)

    assert len(top) <= 2

def test_clear_citations(tracker, sample_documents):
    answer = "Python"
    tracker.extract_citations(answer, sample_documents)

    assert len(tracker.citations) > 0

    tracker.clear_citations()

    assert len(tracker.citations) == 0
