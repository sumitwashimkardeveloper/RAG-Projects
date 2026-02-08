import pytest
from modules.answer_generator import ResponseSynthesizer

@pytest.fixture
def synthesizer():
    return ResponseSynthesizer()

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "metadata": {
                "content": "Python is a programming language",
                "source": "python.org"
            }
        },
        {
            "id": "doc2",
            "metadata": {
                "content": "Machine learning is a subset of artificial intelligence",
                "source": "ml.org"
            }
        }
    ]

def test_synthesize(synthesizer, sample_documents):
    query = "Python machine learning"
    context, sources = synthesizer.synthesize(query, sample_documents)

    assert len(context) > 0
    assert len(sources) > 0

def test_deduplicate_content(synthesizer, sample_documents):
    duplicate_docs = sample_documents + [
        {
            "id": "doc3",
            "metadata": {
                "content": "Python is a programming language",
                "source": "other.org"
            }
        }
    ]

    deduplicated = synthesizer.deduplicate_content(duplicate_docs, similarity_threshold=0.8)

    assert len(deduplicated) <= len(duplicate_docs)

def test_balance_sources(synthesizer, sample_documents):
    many_docs = sample_documents * 3

    balanced = synthesizer.balance_sources(many_docs, max_per_source=1)

    sources_count = {}
    for doc in balanced:
        source = doc["metadata"]["source"]
        sources_count[source] = sources_count.get(source, 0) + 1

    assert all(count <= 1 for count in sources_count.values())

def test_organize_by_relevance(synthesizer, sample_documents):
    docs_with_scores = [
        {**d, "score": 0.9} for d in sample_documents[:1]
    ] + [
        {**d, "score": 0.5} for d in sample_documents[1:]
    ]

    organized = synthesizer.organize_by_relevance(docs_with_scores)

    assert "high_relevance" in organized
    assert "medium_relevance" in organized
    assert "low_relevance" in organized

def test_build_context_string(synthesizer, sample_documents):
    context = synthesizer._build_context_string(sample_documents)

    assert "Python is a programming language" in context
    assert "Machine learning" in context
