import pytest
from modules.critic import Critic, CriticFeedback

@pytest.fixture
def critic(config):
    return Critic(config)

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "score": 0.9,
            "metadata": {
                "content": "Python is a programming language used for data science and machine learning applications",
                "source": "python.org"
            }
        },
        {
            "id": "doc2",
            "score": 0.75,
            "metadata": {
                "content": "Python was created in 1991 by Guido van Rossum",
                "source": "wikipedia.org"
            }
        }
    ]

def test_critic_initialization(critic):
    assert critic.relevance_evaluator is not None
    assert critic.confidence_scorer is not None
    assert critic.gap_detector is not None
    assert critic.completeness_checker is not None

def test_evaluate_basic(critic, sample_documents):
    query = "What is Python?"
    feedback = critic.evaluate(query, sample_documents)

    assert isinstance(feedback, CriticFeedback)
    assert isinstance(feedback.is_relevant, bool)
    assert isinstance(feedback.confidence_score, float)
    assert isinstance(feedback.gaps_identified, list)

def test_evaluate_relevance(critic, sample_documents):
    query = "Python programming"
    is_relevant, score = critic.evaluate_relevance(query, sample_documents)

    assert isinstance(is_relevant, bool)
    assert 0 <= score <= 1

def test_calculate_confidence(critic, sample_documents):
    confidence = critic.calculate_confidence(sample_documents, "test query")

    assert 0 <= confidence <= 1

def test_detect_gaps(critic, sample_documents):
    query = "When and where was Python created?"
    gaps = critic.detect_gaps(query, sample_documents)

    assert isinstance(gaps, list)

def test_check_completeness(critic, sample_documents):
    query = "What is Python?"
    is_complete, score = critic.check_completeness(query, sample_documents)

    assert isinstance(is_complete, bool)
    assert 0 <= score <= 1

def test_get_detailed_report(critic, sample_documents):
    query = "Tell me about Python"
    report = critic.get_detailed_report(query, sample_documents)

    assert "feedback" in report
    assert "relevance_details" in report
    assert "confidence_details" in report
    assert "gap_details" in report
    assert "completeness_details" in report

def test_should_continue_iteration_max_reached(critic):
    feedback = CriticFeedback(
        is_relevant=True,
        confidence_score=0.5,
        should_continue=True
    )

    should_continue = critic.should_continue_iteration(feedback, critic.max_iterations)

    assert should_continue == False

def test_should_continue_iteration_not_reached(critic):
    feedback = CriticFeedback(
        is_relevant=False,
        confidence_score=0.3,
        should_continue=True
    )

    should_continue = critic.should_continue_iteration(feedback, 0)

    assert should_continue == True

def test_get_critique_summary(critic, sample_documents):
    query = "What is Python?"
    feedback = critic.evaluate(query, sample_documents)

    summary = critic.get_critique_summary(feedback)

    assert isinstance(summary, str)
    assert "Summary" in summary or "Relevance" in summary

def test_feedback_suggestions(critic, sample_documents):
    query = "Explain Python comprehensively"
    feedback = critic.evaluate(query, sample_documents)

    assert isinstance(feedback.suggestions, list)

def test_feedback_metadata(critic, sample_documents):
    query = "test"
    feedback = critic.evaluate(query, sample_documents)

    assert isinstance(feedback.metadata, dict)
    assert "evaluation_timestamp" in feedback.metadata or len(feedback.metadata) > 0

def test_critic_with_irrelevant_docs(critic):
    query = "Python"
    documents = [
        {
            "metadata": {
                "content": "Java is a programming language"
            }
        }
    ]

    feedback = critic.evaluate(query, documents)

    assert isinstance(feedback, CriticFeedback)
