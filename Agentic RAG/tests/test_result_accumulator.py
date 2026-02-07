import pytest
from modules.utils import ResultAccumulator

@pytest.fixture
def accumulator():
    return ResultAccumulator(max_documents=10, dedup_threshold=0.9)

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "score": 0.9,
            "metadata": {
                "content": "Python is a programming language",
                "source": "python.org"
            }
        },
        {
            "id": "doc2",
            "score": 0.8,
            "metadata": {
                "content": "Machine learning with Python",
                "source": "ml.org"
            }
        }
    ]

def test_add_results(accumulator, sample_documents):
    accumulator.add_results(sample_documents, iteration=1)

    assert len(accumulator.accumulated) == 2

def test_add_duplicate_results(accumulator, sample_documents):
    accumulator.add_results(sample_documents, iteration=1)
    accumulator.add_results(sample_documents, iteration=2)

    assert len(accumulator.accumulated) == 2
    assert accumulator.accumulated["doc1"].occurrence_count == 2

def test_get_accumulated_results(accumulator, sample_documents):
    accumulator.add_results(sample_documents, iteration=1)

    results = accumulator.get_accumulated_results()

    assert len(results) == 2

def test_get_accumulated_results_limited(accumulator, sample_documents):
    accumulator.add_results(sample_documents, iteration=1)

    results = accumulator.get_accumulated_results(top_k=1)

    assert len(results) == 1

def test_deduplicate_similar(accumulator):
    docs = [
        {
            "id": "doc1",
            "score": 0.9,
            "metadata": {
                "content": "Python is a programming language",
                "source": "source1"
            }
        },
        {
            "id": "doc2",
            "score": 0.8,
            "metadata": {
                "content": "Python is a programming language",
                "source": "source2"
            }
        }
    ]

    accumulator.add_results(docs, iteration=1)
    removed = accumulator.deduplicate_similar()

    assert removed >= 0

def test_get_coverage_stats(accumulator, sample_documents):
    accumulator.add_results(sample_documents, iteration=1)

    stats = accumulator.get_coverage_stats()

    assert "total_unique" in stats
    assert "total_occurrences" in stats
    assert "sources_count" in stats

def test_get_result_ranking(accumulator, sample_documents):
    accumulator.add_results(sample_documents, iteration=1)

    ranking = accumulator.get_result_ranking()

    assert len(ranking) == 2
    assert all(len(r) == 3 for r in ranking)

def test_clear(accumulator, sample_documents):
    accumulator.add_results(sample_documents, iteration=1)
    accumulator.clear()

    assert len(accumulator.accumulated) == 0

def test_get_iteration_deltas(accumulator, sample_documents):
    accumulator.add_results(sample_documents, iteration=1)
    accumulator.add_results(sample_documents[:1], iteration=2)

    deltas = accumulator.get_iteration_deltas()

    assert 1 in deltas
    assert 2 in deltas

def test_get_summary(accumulator, sample_documents):
    accumulator.add_results(sample_documents, iteration=1)

    summary = accumulator.get_summary()

    assert "coverage" in summary
    assert "top_results" in summary
    assert "current_iteration" in summary
