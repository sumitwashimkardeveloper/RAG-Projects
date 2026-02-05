import pytest
from modules.retriever import Deduplicator, ResultFilter, FilterPipeline

@pytest.fixture
def sample_results():
    return [
        {"id": "doc1", "score": 0.9, "metadata": {"source": "source1", "content": "Python data science", "length": 100}},
        {"id": "doc1", "score": 0.88, "metadata": {"source": "source1", "content": "Python data science", "length": 100}},
        {"id": "doc2", "score": 0.7, "metadata": {"source": "source2", "content": "JavaScript web dev", "length": 80}},
        {"id": "doc3", "score": 0.5, "metadata": {"source": "source1", "content": "Java backend", "length": 120}}
    ]

def test_deduplication_by_id(sample_results):
    deduplicated = Deduplicator.deduplicate_by_id(sample_results)

    assert len(deduplicated) == 3
    ids = {r["id"] for r in deduplicated}
    assert len(ids) == 3

def test_deduplication_by_content(sample_results):
    deduplicated = Deduplicator.deduplicate_by_content(sample_results)

    assert len(deduplicated) < len(sample_results)

def test_filter_by_score(sample_results):
    filtered = ResultFilter.filter_by_score(sample_results, threshold=0.7)

    assert len(filtered) == 2
    assert all(r.get("score", 0) >= 0.7 for r in filtered)

def test_filter_by_metadata(sample_results):
    filters = {"source": "source1"}
    filtered = ResultFilter.filter_by_metadata(sample_results, filters)

    for result in filtered:
        assert result["metadata"]["source"] == "source1"

def test_filter_by_length(sample_results):
    filtered = ResultFilter.filter_by_length(sample_results, min_length=5, max_length=110)

    assert len(filtered) > 0
    for result in filtered:
        content = result["metadata"]["content"]
        word_count = len(content.split())
        assert 5 <= word_count <= 110

def test_filter_by_source(sample_results):
    filtered = ResultFilter.filter_by_source(sample_results, ["source1"])

    for result in filtered:
        assert "source1" in result["metadata"]["source"]

def test_filter_by_custom(sample_results):
    filtered = ResultFilter.filter_by_custom(
        sample_results,
        lambda r: r.get("score", 0) > 0.6
    )

    assert all(r.get("score", 0) > 0.6 for r in filtered)

def test_filter_pipeline(sample_results):
    pipeline = FilterPipeline()
    pipeline.add_filter("high_score", lambda r: ResultFilter.filter_by_score(r, 0.7))
    pipeline.add_filter("source_filter", lambda r: ResultFilter.filter_by_source(r, ["source1"]))

    results = pipeline.apply(sample_results)

    assert all(r.get("score", 0) >= 0.7 for r in results)
    assert all("source1" in r["metadata"]["source"] for r in results)

def test_filter_pipeline_reset():
    pipeline = FilterPipeline()
    pipeline.add_filter("test1", lambda r: r)
    pipeline.add_filter("test2", lambda r: r)

    assert len(pipeline.filters) == 2

    pipeline.reset()

    assert len(pipeline.filters) == 0

def test_similarity_calculation():
    text1 = "Python is a programming language"
    text2 = "Python is a programming language"
    similarity = Deduplicator._calculate_similarity(text1, text2)

    assert similarity == 1.0

def test_similarity_different():
    text1 = "Python"
    text2 = "Java"
    similarity = Deduplicator._calculate_similarity(text1, text2)

    assert similarity == 0.0
