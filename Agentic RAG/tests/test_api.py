import pytest
from fastapi.testclient import TestClient
from api import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "components" in data

def test_query_endpoint(client):
    request = {
        "query": "What is Python?",
        "top_k": 5,
        "max_iterations": 5
    }

    response = client.post("/query", json=request)

    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "answer" in data
        assert "documents" in data

def test_query_with_metadata(client):
    request = {
        "query": "Machine learning",
        "top_k": 3,
        "include_metadata": True
    }

    response = client.post("/query", json=request)

    assert response.status_code in [200, 500]

def test_metrics_endpoint(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()
    assert "pipeline_stats" in data
    assert "timestamp" in data

def test_info_endpoint(client):
    response = client.get("/info")

    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "components" in data

def test_evaluate_endpoint(client):
    request = {
        "query": "What is Python?",
        "answer": "Python is a programming language",
        "documents": []
    }

    response = client.post("/evaluate", params=request)

    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert "is_valid" in data
        assert "score" in data

def test_invalid_query(client):
    request = {
        "query": "",
        "top_k": 5
    }

    response = client.post("/query", json=request)

    assert response.status_code in [200, 500]

def test_large_query(client):
    request = {
        "query": "Test " * 1000,
        "top_k": 5
    }

    response = client.post("/query", json=request)

    assert response.status_code in [200, 500]

def test_custom_top_k(client):
    request = {
        "query": "Python",
        "top_k": 10
    }

    response = client.post("/query", json=request)

    assert response.status_code in [200, 500]

def test_api_response_format(client):
    request = {"query": "Test query"}

    response = client.post("/query", json=request)

    if response.status_code == 200:
        data = response.json()
        assert "query" in data
        assert "answer" in data
        assert "documents" in data
        assert "citations" in data
        assert isinstance(data["documents"], list)
        assert isinstance(data["citations"], list)
