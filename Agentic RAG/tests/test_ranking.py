import pytest
from modules.retriever import RankingEngine, ScoreNormalizer, ResultScorer

@pytest.fixture
def sample_results():
    return [
        {"id": "doc1", "score": 0.9, "metadata": {"content": "Python data science"}},
        {"id": "doc2", "score": 0.7, "metadata": {"content": "JavaScript web dev"}},
        {"id": "doc3", "score": 0.5, "metadata": {"content": "Java backend"}}
    ]

@pytest.fixture
def ranking_engine():
    return RankingEngine()

def test_ranking_engine_basic(ranking_engine, sample_results):
    ranking_engine.add_criteria(
        "base_score",
        1.0,
        lambda r: r.get("score", 0)
    )

    results = ranking_engine.rank(sample_results)

    assert results[0]["id"] == "doc1"
    assert results[-1]["id"] == "doc3"

def test_multiple_ranking_criteria(ranking_engine, sample_results):
    ranking_engine.add_criteria("base_score", 0.7, lambda r: r.get("score", 0))
    ranking_engine.add_criteria("length", 0.3, lambda r: len(r.get("metadata", {}).get("content", "")) / 100)

    results = ranking_engine.rank(sample_results)

    assert all("combined_score" in r for r in results)
    assert all("ranking_scores" in r for r in results)

def test_score_normalization_minmax(sample_results):
    normalized = ScoreNormalizer.normalize_minmax(sample_results)

    scores = [r.get("normalized_score") for r in normalized]
    assert min(scores) >= 0 and max(scores) <= 1

def test_score_normalization_zscore(sample_results):
    normalized = ScoreNormalizer.normalize_zscore(sample_results)

    assert all("z_score" in r for r in normalized)

def test_result_scorer_relevance():
    result = {"metadata": {"content": "Python machine learning algorithms"}}
    score = ResultScorer.score_relevance(result, ["python", "machine"])

    assert score > 0

def test_result_scorer_authority():
    result_good = {"metadata": {"source": "arxiv.org paper"}}
    result_bad = {"metadata": {"source": "random.com"}}

    score_good = ResultScorer.score_authority(result_good)
    score_bad = ResultScorer.score_authority(result_bad)

    assert score_good >= score_bad

def test_result_scorer_length():
    result_short = {"metadata": {"content": "short"}}
    result_long = {"metadata": {"content": " ".join(["word"] * 100)}}

    score_short = ResultScorer.score_length(result_short)
    score_long = ResultScorer.score_length(result_long)

    assert score_short > 0 and score_long > 0

def test_ranking_empty_results(ranking_engine):
    results = ranking_engine.rank([])

    assert results == []

def test_ranking_engine_reset(ranking_engine, sample_results):
    ranking_engine.add_criteria("test", 1.0, lambda r: r.get("score", 0))
    ranking_engine.reset_criteria()

    assert len(ranking_engine.criteria) == 0
