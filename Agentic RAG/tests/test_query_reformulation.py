import pytest
from modules.query_rewriter import QueryReformulator

@pytest.fixture
def reformulator():
    return QueryReformulator()

def test_reformulate_basic(reformulator):
    query = "python programming"
    reformulated = reformulator.reformulate(query)

    assert len(reformulated) >= 1
    assert reformulated[0] == query

def test_reformulate_temporal(reformulator):
    query = "python"
    reformulated = reformulator.reformulate(query, gap_type="temporal")

    assert len(reformulated) > 0
    reformulated_str = " ".join(reformulated).lower()
    assert "when" in reformulated_str or "time" in reformulated_str or len(reformulated) > 1

def test_reformulate_spatial(reformulator):
    query = "cloud computing"
    reformulated = reformulator.reformulate(query, gap_type="spatial")

    assert len(reformulated) > 0

def test_reformulate_causal(reformulator):
    query = "climate change"
    reformulated = reformulator.reformulate(query, gap_type="causal")

    reformulated_str = " ".join(reformulated).lower()
    assert "why" in reformulated_str or "cause" in reformulated_str or len(reformulated) > 1

def test_reformulate_procedural(reformulator):
    query = "machine learning"
    reformulated = reformulator.reformulate(query, gap_type="procedural")

    reformulated_str = " ".join(reformulated).lower()
    assert "how" in reformulated_str or "process" in reformulated_str or len(reformulated) > 1

def test_create_structural_variants(reformulator):
    query = "What is Python?"
    variants = reformulator._create_structural_variants(query)

    assert len(variants) > 0
    variants_str = " ".join(variants).lower()
    assert "python" in variants_str

def test_reformulate_based_on_gaps(reformulator):
    query = "Python"
    gaps = ["temporal_gap: missing when information", "causal_gap: missing why information"]
    reformulated = reformulator.reformulate_based_on_gaps(query, gaps)

    assert len(reformulated) >= 1

def test_add_custom_pattern(reformulator):
    reformulator.add_pattern("custom", "Custom pattern with {subject}")
    reformulated = reformulator.reformulate("test", gap_type="custom")

    assert len(reformulated) >= 1

def test_get_reformulation_explanation(reformulator):
    original = "Python"
    reformulated = "Python programming language"
    explanation = reformulator.get_reformulation_explanation(original, reformulated)

    assert explanation != ""
    assert isinstance(explanation, str)
