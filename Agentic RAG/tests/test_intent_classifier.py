import pytest
from modules.planner import IntentClassifier, QueryIntent

@pytest.fixture
def classifier():
    return IntentClassifier()

def test_classify_definition_query(classifier):
    query = "What is machine learning?"
    intent, confidence = classifier.classify(query)

    assert intent == QueryIntent.DEFINITION
    assert confidence > 0.0

def test_classify_how_to_query(classifier):
    query = "How do I set up a Python environment?"
    intent, confidence = classifier.classify(query)

    assert intent == QueryIntent.HOW_TO
    assert confidence > 0.0

def test_classify_comparison_query(classifier):
    query = "What's the difference between Python and JavaScript?"
    intent, confidence = classifier.classify(query)

    assert intent == QueryIntent.COMPARISON
    assert confidence > 0.0

def test_classify_reasoning_query(classifier):
    query = "Why is climate change happening?"
    intent, confidence = classifier.classify(query)

    assert intent == QueryIntent.REASONING
    assert confidence > 0.0

def test_classify_factual_query(classifier):
    query = "When was Python created?"
    intent, confidence = classifier.classify(query)

    assert intent == QueryIntent.FACTUAL
    assert confidence > 0.0

def test_classify_summary_query(classifier):
    query = "Summarize the main points of this article"
    intent, confidence = classifier.classify(query)

    assert intent == QueryIntent.SUMMARY
    assert confidence > 0.0

def test_confidence_score_range(classifier):
    queries = [
        "What is AI?",
        "Hello world",
        "How to learn programming?",
    ]

    for query in queries:
        intent, confidence = classifier.classify(query)
        assert 0 <= confidence <= 1

def test_get_intent_features(classifier):
    query = "What is machine learning and how does it work?"
    features = classifier.get_intent_features(query)

    assert "intent" in features
    assert "confidence" in features
    assert "is_question" in features
    assert "word_count" in features
    assert "keyword_count" in features
    assert features["is_question"] == True

def test_unknown_intent_defaults_to_search(classifier):
    query = "xyz abc def ghij"
    intent, confidence = classifier.classify(query)

    assert intent == QueryIntent.SEARCH or confidence <= 0.5
