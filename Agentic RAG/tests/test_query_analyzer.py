import pytest
from modules.planner import QueryAnalyzer

@pytest.fixture
def analyzer():
    return QueryAnalyzer()

def test_analyze_simple_query(analyzer):
    query = "What is Python?"
    analysis = analyzer.analyze(query)

    assert "original_query" in analysis
    assert "normalized_query" in analysis
    assert "keywords" in analysis
    assert "entities" in analysis
    assert "sub_queries" in analysis

def test_analyze_extracts_keywords(analyzer):
    query = "machine learning algorithms and neural networks"
    analysis = analyzer.analyze(query)

    keywords = analysis["keywords"]
    assert "machine" in keywords
    assert "learning" in keywords
    assert "algorithms" in keywords

def test_analyze_extracts_entities(analyzer):
    query = "Python and JavaScript are programming languages"
    analysis = analyzer.analyze(query)

    entities = analysis["entities"]
    assert any(e in entities for e in ["Python", "JavaScript"])

def test_analyze_detects_multiple_parts(analyzer):
    query = "What is AI and how does it work?"
    analysis = analyzer.analyze(query)

    assert analysis["has_multiple_parts"] == True
    assert len(analysis["sub_queries"]) > 1

def test_analyze_calculates_complexity(analyzer):
    simple_query = "What is AI?"
    complex_query = "What is artificial intelligence, and how does it differ from machine learning, particularly in the context of neural networks and deep learning?"

    simple_analysis = analyzer.analyze(simple_query)
    complex_analysis = analyzer.analyze(complex_query)

    assert complex_analysis["complexity"] > simple_analysis["complexity"]

def test_analyze_identifies_focus_areas(analyzer):
    query = "How do I install Python?"
    analysis = analyzer.analyze(query)

    sub_queries = analysis["sub_queries"]
    assert len(sub_queries) > 0
    assert any(sq.focus_area in ["process", "how_to"] for sq in sub_queries)

def test_decompose_with_conjunctions(analyzer):
    query = "machine learning and deep learning"
    analysis = analyzer.analyze(query)

    sub_queries = analysis["sub_queries"]
    assert len(sub_queries) >= 1

def test_normalize_whitespace(analyzer):
    query = "What   is    machine    learning?"
    analysis = analyzer.analyze(query)

    assert "  " not in analysis["normalized_query"]
