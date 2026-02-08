import pytest
from modules.answer_generator import AnswerValidator

@pytest.fixture
def validator():
    return AnswerValidator()

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "metadata": {
                "content": "Python is a programming language. It is used for data science.",
                "source": "python.org"
            }
        }
    ]

def test_validate_good_answer(validator, sample_documents):
    answer = "Python is a programming language used for data science and machine learning."
    query = "What is Python used for?"

    is_valid, score, issues = validator.validate(answer, query, sample_documents)

    assert score > 0.5

def test_validate_too_short_answer(validator, sample_documents):
    answer = "Python."
    query = "What is Python?"

    is_valid, score, issues = validator.validate(answer, query, sample_documents)

    assert any("too short" in issue.lower() for issue in issues)

def test_validate_irrelevant_answer(validator, sample_documents):
    answer = "Java is a programming language used for backend development and enterprise applications."
    query = "What is Python?"

    is_valid, score, issues = validator.validate(answer, query, sample_documents)

    assert len(issues) > 0

def test_validate_length(validator):
    short = "hi"
    long = " ".join(["word"] * 1000)

    is_valid_short, _ = validator._validate_length(short)
    is_valid_long, _ = validator._validate_length(long)

    assert not is_valid_short
    assert not is_valid_long

def test_validate_relevance(validator):
    answer = "Python is a programming language"
    query = "What is Python?"

    is_valid, _ = validator._validate_relevance(answer, query)

    assert is_valid

def test_validate_structure(validator):
    answer = "python is cool"
    is_valid, issues = validator._validate_structure(answer)

    assert not is_valid
    assert len(issues) > 0

def test_get_quality_score_breakdown(validator, sample_documents):
    answer = "Python is a programming language used for data science."
    query = "What is Python used for?"

    breakdown = validator.get_quality_score_breakdown(answer, query, sample_documents)

    assert "overall" in breakdown
    assert "length" in breakdown
    assert "relevance" in breakdown
