import pytest
from modules.query_rewriter import QueryRewriter, RewrittenQuery

@pytest.fixture
def rewriter(config):
    return QueryRewriter(config)

@pytest.fixture
def sample_feedback():
    return {
        "gaps_identified": ["temporal_gap", "causal_gap"],
        "confidence_score": 0.5
    }

def test_rewriter_initialization(rewriter):
    assert rewriter.expander is not None
    assert rewriter.reformulator is not None
    assert rewriter.diversifier is not None
    assert rewriter.learning_engine is not None

def test_rewrite_basic(rewriter):
    query = "Python"
    rewritten = rewriter.rewrite(query)

    assert isinstance(rewritten, RewrittenQuery)
    assert rewritten.original_query == query
    assert rewritten.rewritten_query != "" or rewritten.rewritten_query == query

def test_rewrite_with_feedback(rewriter, sample_feedback):
    query = "Python"
    rewritten = rewriter.rewrite(query, feedback=sample_feedback)

    assert isinstance(rewritten, RewrittenQuery)
    assert rewritten.strategy != ""

def test_expand_query(rewriter):
    query = "python"
    expanded = rewriter.expand_query(query)

    assert len(expanded) >= 1
    assert expanded[0] == query

def test_reformulate_query(rewriter):
    query = "Python"
    reformulated = rewriter.reformulate_query(query)

    assert len(reformulated) >= 1

def test_reformulate_with_gaps(rewriter):
    query = "Python"
    gaps = ["temporal_gap", "causal_gap"]
    reformulated = rewriter.reformulate_query(query, gaps)

    assert len(reformulated) >= 1

def test_diversify_query(rewriter):
    query = "Python"
    diversified = rewriter.diversify_query(query)

    assert len(diversified) > 0

def test_record_rewrite_success(rewriter):
    original = "Python"
    rewritten = "Python programming"
    rewriter.record_rewrite_success(original, rewritten, 0.85)

    stats = rewriter.get_rewrite_statistics()
    assert stats["total_reformulations"] >= 1

def test_get_alternative_queries(rewriter):
    query = "machine learning"
    alternatives = rewriter.get_alternative_queries(query)

    assert isinstance(alternatives, list)
    assert len(alternatives) > 0

def test_create_query_variations(rewriter):
    query = "Python"
    variations = rewriter.create_query_variations(query)

    assert "expanded" in variations
    assert "reformulated" in variations
    assert "diversified" in variations
    assert "learned" in variations

def test_get_learning_insights(rewriter):
    rewriter.record_rewrite_success("test", "reformulated", 0.8)

    insights = rewriter.get_learning_insights()

    assert "statistics" in insights
    assert "top_reformulations" in insights

def test_rewrite_strategy_selection(rewriter):
    rewriter.record_rewrite_success("test query", "learned reformulation", 0.9)

    rewritten = rewriter.rewrite("test query")

    assert rewritten.strategy == "learned" or rewritten.strategy in ["gap_based", "expansion", "diversification"]

def test_rewritten_query_confidence(rewriter, sample_feedback):
    query = "Python"
    rewritten = rewriter.rewrite(query, feedback=sample_feedback)

    assert 0 <= rewritten.confidence_score <= 1
    assert rewritten.confidence_score > sample_feedback["confidence_score"]

def test_rewritten_query_alternatives(rewriter):
    query = "Python"
    rewritten = rewriter.rewrite(query)

    assert isinstance(rewritten.alternatives, list)
    assert len(rewritten.alternatives) <= 3
