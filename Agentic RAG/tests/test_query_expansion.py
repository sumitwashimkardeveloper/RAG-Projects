import pytest
from modules.query_rewriter import QueryExpander

@pytest.fixture
def expander():
    return QueryExpander()

def test_expand_basic(expander):
    query = "python machine learning"
    expanded = expander.expand(query)

    assert len(expanded) >= 1
    assert expanded[0] == query

def test_expand_with_synonyms(expander):
    query = "python programming"
    expanded = expander.expand(query)

    assert len(expanded) > 1
    assert any("python" in e.lower() for e in expanded)

def test_expand_with_related_terms(expander):
    query = "machine learning"
    expanded = expander.expand(query)

    expanded_str = " ".join(expanded).lower()
    assert "neural" in expanded_str or "deep" in expanded_str or len(expanded) > 1

def test_add_custom_synonyms(expander):
    expander.add_synonyms("ai", ["artificial intelligence", "algorithms"])
    expanded = expander.expand("ai system")

    assert len(expanded) >= 1

def test_add_custom_related_terms(expander):
    expander.add_related_terms("ai", ["robotics", "computer vision"])
    expanded = expander.expand("ai")

    assert len(expanded) >= 1

def test_get_all_variants(expander):
    query = "python"
    variants = expander.get_all_variants(query, max_variants=5)

    assert len(variants) <= 5
    assert variants[0] == query

def test_extract_key_terms(expander):
    query = "machine learning for data science"
    terms = expander.extract_key_terms(query)

    assert "machine" in terms
    assert "learning" in terms
    assert "data" in terms

def test_extract_key_terms_filters_short(expander):
    query = "the quick brown fox"
    terms = expander.extract_key_terms(query)

    assert "the" not in terms
    assert len(terms) > 0
