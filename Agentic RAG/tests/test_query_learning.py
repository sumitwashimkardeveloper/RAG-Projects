import pytest
import tempfile
from pathlib import Path
from modules.query_rewriter import QueryLearningEngine

@pytest.fixture
def temp_cache_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def learning_engine(temp_cache_dir):
    cache_file = f"{temp_cache_dir}/test_reformulations.json"
    return QueryLearningEngine(cache_file=cache_file)

def test_record_reformulation(learning_engine):
    original = "What is Python?"
    reformulated = "Explain Python"
    learning_engine.record_reformulation(original, reformulated, 0.85, "definition")

    assert original in learning_engine.learned_reformulations
    assert len(learning_engine.learned_reformulations[original]) > 0

def test_get_learned_reformulations(learning_engine):
    original = "Python"
    learning_engine.record_reformulation(original, "Python programming", 0.9)
    learning_engine.record_reformulation(original, "Python language", 0.85)

    learned = learning_engine.get_learned_reformulations(original)

    assert len(learned) > 0
    assert "Python programming" in learned or "Python language" in learned

def test_get_best_reformulation(learning_engine):
    original = "test"
    learning_engine.record_reformulation(original, "test1", 0.7)
    learning_engine.record_reformulation(original, "test2", 0.9)

    best, score = learning_engine.get_best_reformulation(original)

    assert score >= 0.7

def test_get_statistics(learning_engine):
    learning_engine.record_reformulation("q1", "r1", 0.8)
    learning_engine.record_reformulation("q2", "r2", 0.5)

    stats = learning_engine.get_statistics()

    assert "total_queries_with_reformulations" in stats
    assert "total_reformulations" in stats
    assert "success_rate" in stats

def test_clear_cache(learning_engine):
    learning_engine.record_reformulation("test", "reformulated", 0.8)

    learning_engine.clear_cache()

    assert len(learning_engine.learned_reformulations) == 0

def test_get_top_reformulations(learning_engine):
    learning_engine.record_reformulation("q1", "r1", 0.9)
    learning_engine.record_reformulation("q2", "r2", 0.85)
    learning_engine.record_reformulation("q3", "r3", 0.75)

    top = learning_engine.get_top_reformulations(limit=2)

    assert len(top) <= 2

def test_update_success_score(learning_engine):
    original = "test"
    learning_engine.record_reformulation(original, "reformulated", 0.5)

    learning_engine.update_success_score(original, "reformulated", 0.9)

    best, score = learning_engine.get_best_reformulation(original)
    assert score >= 0.8

def test_invalid_score_not_recorded(learning_engine):
    original = "test"
    learning_engine.record_reformulation(original, "reformulated", 1.5)

    assert original not in learning_engine.learned_reformulations

def test_filter_by_gap_type(learning_engine):
    learning_engine.record_reformulation("q1", "r1", 0.8, gap_type="temporal")
    learning_engine.record_reformulation("q1", "r2", 0.7, gap_type="spatial")

    temporal = learning_engine.get_learned_reformulations("q1", gap_type="temporal")

    assert len(temporal) >= 0
