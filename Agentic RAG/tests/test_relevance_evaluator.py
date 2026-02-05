import pytest
from modules.critic import RelevanceEvaluator

@pytest.fixture
def evaluator():
    return RelevanceEvaluator()

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "metadata": {
                "content": "Python is a programming language used for data science and machine learning",
                "source": "python.org"
            }
        },
        {
            "id": "doc2",
            "metadata": {
                "content": "JavaScript",
                "source": "js.org"
            }
        },
        {
            "id": "doc3",
            "metadata": {
                "content": "Machine learning algorithms and neural networks explained in detail",
                "source": "ml.org"
            }
        }
    ]

def test_evaluate_relevant_query(evaluator, sample_documents):
    query = "What is Python used for?"
    is_relevant, score = evaluator.evaluate(query, sample_documents[0])

    assert is_relevant == True
    assert score > 0.4

def test_evaluate_irrelevant_query(evaluator, sample_documents):
    query = "What is Java?"
    is_relevant, score = evaluator.evaluate(query, sample_documents[1])

    assert is_relevant == False or score < 0.5

def test_evaluate_batch(evaluator, sample_documents):
    query = "Python machine learning"
    results = evaluator.evaluate_batch(query, sample_documents)

    assert len(results) == len(sample_documents)
    assert all(isinstance(r, tuple) for r in results)

def test_find_most_relevant(evaluator, sample_documents):
    query = "machine learning"
    most_relevant = evaluator.find_most_relevant(query, sample_documents)

    assert most_relevant != {}
    assert "content" in most_relevant.get("metadata", {})

def test_filter_by_relevance(evaluator, sample_documents):
    query = "Python programming"
    relevant = evaluator.filter_by_relevance(query, sample_documents, threshold=0.3)

    assert len(relevant) >= 1
    assert all("relevance_score" in doc for doc in relevant)

def test_entity_matching(evaluator):
    query = "What did Albert Einstein discover?"
    document = {
        "metadata": {
            "content": "Albert Einstein developed the theory of relativity"
        }
    }

    is_relevant, score = evaluator.evaluate(query, document)

    assert score > 0

def test_score_range(evaluator, sample_documents):
    query = "test query"
    for doc in sample_documents:
        _, score = evaluator.evaluate(query, doc)
        assert 0 <= score <= 1
