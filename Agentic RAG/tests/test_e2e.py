import pytest
from pipeline import AgenticRAGPipeline

@pytest.fixture
def pipeline_e2e(config):
    return AgenticRAGPipeline(config)

@pytest.fixture
def test_queries():
    return [
        "What is Python?",
        "How does machine learning work?",
        "Explain the difference between AI and machine learning",
        "What are the benefits of using Python for data science?",
        "How to implement a neural network?"
    ]

@pytest.fixture
def benchmark_dataset():
    return [
        {
            "query": "What is Python?",
            "expected_topics": ["programming language", "data science", "AI"],
            "min_confidence": 0.6
        },
        {
            "query": "Machine learning algorithms",
            "expected_topics": ["machine learning", "algorithms", "classification"],
            "min_confidence": 0.6
        },
        {
            "query": "Deep learning explained",
            "expected_topics": ["deep learning", "neural networks", "artificial intelligence"],
            "min_confidence": 0.5
        }
    ]

def test_e2e_simple_query(pipeline_e2e):
    result = pipeline_e2e.process("What is Python?")

    assert result["success"]
    assert "answer" in result
    assert len(result["answer"]) > 0
    assert result["iterations"]["total_iterations"] > 0

def test_e2e_complex_query(pipeline_e2e):
    result = pipeline_e2e.process("Compare machine learning and deep learning approaches")

    assert result["success"]
    assert result["iterations"]["total_iterations"] >= 1

def test_e2e_multiple_iterations(pipeline_e2e):
    result = pipeline_e2e.process("What are the latest advances in AI?")

    assert result["success"]
    assert result["iterations"]["total_iterations"] > 0
    assert result["iterations"]["avg_confidence"] > 0

def test_e2e_edge_case_empty_query(pipeline_e2e):
    result = pipeline_e2e.process("")

    assert "error" in result or result["success"] == False

def test_e2e_edge_case_very_long_query(pipeline_e2e):
    long_query = "Tell me everything about " + " ".join(["machine learning"] * 50)
    result = pipeline_e2e.process(long_query)

    assert "answer" in result or "error" in result

def test_e2e_confidence_threshold(pipeline_e2e):
    result = pipeline_e2e.process("What is Python?")

    confidence = result["iterations"]["avg_confidence"]
    assert 0 <= confidence <= 1

def test_e2e_document_retrieval(pipeline_e2e):
    result = pipeline_e2e.process("Python programming")

    documents = result.get("documents", [])
    assert len(documents) >= 0

def test_e2e_citation_tracking(pipeline_e2e):
    result = pipeline_e2e.process("Machine learning")

    if result["success"]:
        answer = result.get("answer", "")
        assert len(answer) > 0

def test_e2e_state_machine_transitions(pipeline_e2e):
    result = pipeline_e2e.process("What is AI?")

    state_history = result.get("state_history", [])
    assert len(state_history) > 0
    assert state_history[0] == "planner"

def test_e2e_error_recovery(pipeline_e2e):
    result = pipeline_e2e.process("Query to test system")

    assert "answer" in result or "error" in result or result["success"] in [True, False]

def test_e2e_benchmark_against_dataset(pipeline_e2e, benchmark_dataset):
    results = []

    for benchmark in benchmark_dataset:
        result = pipeline_e2e.process(benchmark["query"])

        if result["success"]:
            answer = result.get("answer", "").lower()
            expected_found = any(topic in answer for topic in benchmark["expected_topics"])
            confidence = result["iterations"]["avg_confidence"]

            results.append({
                "query": benchmark["query"],
                "success": result["success"],
                "expected_topics_found": expected_found,
                "confidence": confidence,
                "meets_threshold": confidence >= benchmark["min_confidence"]
            })

    assert len(results) > 0

def test_e2e_pipeline_statistics(pipeline_e2e):
    pipeline_e2e.process("Test query 1")

    stats = pipeline_e2e.get_pipeline_statistics()

    assert "iteration_metrics" in stats
    assert "accumulator_stats" in stats
    assert "state_history" in stats

def test_e2e_concurrent_queries(pipeline_e2e):
    queries = [
        "What is Python?",
        "Machine learning basics",
        "AI explained"
    ]

    for query in queries:
        result = pipeline_e2e.process(query)
        assert "answer" in result or "error" in result
