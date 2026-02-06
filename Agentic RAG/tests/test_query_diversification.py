import pytest
from modules.query_rewriter import QueryDiversifier

@pytest.fixture
def diversifier():
    return QueryDiversifier()

def test_diversify_basic(diversifier):
    query = "python programming"
    variants = diversifier.diversify(query, num_variants=3)

    assert len(variants) <= 3
    assert variants[0] == query

def test_create_alternative_phrasings(diversifier):
    query = "What is Python?"
    phrasings = diversifier.create_alternative_phrasings(query)

    assert len(phrasings) > 0
    assert all("python" in p.lower() for p in phrasings)

def test_convert_to_imperative(diversifier):
    query = "What is Python?"
    imperative = diversifier._convert_to_imperative(query)

    assert imperative != query
    assert len(imperative) > 0

def test_convert_to_interrogative(diversifier):
    query = "Python programming"
    interrogative = diversifier._convert_to_interrogative(query)

    assert interrogative.endswith("?")

def test_convert_to_declarative(diversifier):
    query = "What is Python?"
    declarative = diversifier._convert_to_declarative(query)

    assert declarative.endswith(".")

def test_create_aspect_variants(diversifier):
    query = "machine learning"
    aspects = diversifier.create_aspect_variants(query)

    assert len(aspects) > 0
    assert all("machine learning" in a for a in aspects)

def test_create_scope_variants(diversifier):
    query = "Python"
    scopes = diversifier.create_scope_variants(query)

    assert len(scopes) > 0
    assert all("Python" in s for s in scopes)

def test_diversify_by_intent(diversifier):
    query = "data science"
    intents = diversifier.diversify_by_intent(query)

    assert len(intents) > 0

def test_generate_complementary_queries(diversifier):
    query = "machine learning"
    complementary = diversifier.generate_complementary_queries(query)

    assert len(complementary) > 0
    assert all("machine learning" in q or q.endswith("machine learning") for q in complementary)

def test_rank_variants(diversifier):
    query = "python"
    variants = ["python programming", "python language", "javascript"]
    ranked = diversifier.rank_variants(variants, query)

    assert len(ranked) > 0
    assert ranked[0] != "javascript"
