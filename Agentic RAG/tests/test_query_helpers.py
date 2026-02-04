import pytest
from modules.utils.query_helpers import QueryHelper

def test_normalize_query():
    query = "  Hello   World  "
    normalized = QueryHelper.normalize_query(query)

    assert normalized == "hello world"
    assert "  " not in normalized

def test_extract_keywords():
    query = "What is the best machine learning algorithm?"
    keywords = QueryHelper.extract_keywords(query)

    assert "best" in keywords
    assert "machine" in keywords
    assert "learning" in keywords
    assert "the" not in keywords

def test_split_query():
    query = "python programming tutorial"
    parts = QueryHelper.split_query(query)

    assert len(parts) == 3
    assert "python" in parts
    assert "programming" in parts

def test_build_filter():
    filters = {
        "category": "news",
        "year": 2024,
        "tags": ["python", "ai"]
    }
    filter_dict = QueryHelper.build_filter(filters)

    assert "category" in filter_dict
    assert "year" in filter_dict
    assert "tags" in filter_dict

def test_merge_results():
    results1 = [
        {"id": "doc1", "score": 0.9},
        {"id": "doc2", "score": 0.8}
    ]
    results2 = [
        {"id": "doc1", "score": 0.7},
        {"id": "doc3", "score": 0.6}
    ]

    merged = QueryHelper.merge_results([results1, results2])

    doc_ids = {r["id"] for r in merged}
    assert "doc1" in doc_ids
    assert "doc2" in doc_ids
    assert "doc3" in doc_ids

def test_deduplicate_results():
    results = [
        {"id": "doc1", "content": "a"},
        {"id": "doc1", "content": "a"},
        {"id": "doc2", "content": "b"}
    ]

    deduplicated = QueryHelper.deduplicate_results(results)

    assert len(deduplicated) == 2

def test_filter_by_score():
    results = [
        {"id": "doc1", "score": 0.9},
        {"id": "doc2", "score": 0.5},
        {"id": "doc3", "score": 0.3}
    ]

    filtered = QueryHelper.filter_by_score(results, threshold=0.6)

    assert len(filtered) == 1
    assert filtered[0]["id"] == "doc1"

def test_limit_results():
    results = [
        {"id": f"doc{i}", "score": 0.9 - (i * 0.1)} for i in range(10)
    ]

    limited = QueryHelper.limit_results(results, limit=5)

    assert len(limited) == 5

def test_sort_results():
    results = [
        {"id": "doc1", "score": 0.5},
        {"id": "doc2", "score": 0.9},
        {"id": "doc3", "score": 0.7}
    ]

    sorted_results = QueryHelper.sort_results(results, key="score", reverse=True)

    assert sorted_results[0]["score"] == 0.9
    assert sorted_results[-1]["score"] == 0.5
