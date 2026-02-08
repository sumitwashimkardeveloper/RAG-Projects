import pytest
from unittest.mock import Mock, patch
from modules.answer_generator import AnswerGenerator, GeneratedAnswer

@pytest.fixture
def generator(config):
    return AnswerGenerator(config)

@pytest.fixture
def sample_documents():
    return [
        {
            "id": "doc1",
            "score": 0.9,
            "context_score": 0.85,
            "metadata": {
                "content": "Python is a high-level programming language with dynamic typing and automatic memory management.",
                "source": "python.org"
            }
        },
        {
            "id": "doc2",
            "score": 0.8,
            "context_score": 0.8,
            "metadata": {
                "content": "Machine learning is a subset of artificial intelligence that focuses on learning from data.",
                "source": "ml.org"
            }
        }
    ]

def test_generator_initialization(generator):
    assert generator.context_ranker is not None
    assert generator.prompt_manager is not None
    assert generator.synthesizer is not None
    assert generator.citation_tracker is not None
    assert generator.validator is not None

def test_rank_context(generator, sample_documents):
    query = "Python machine learning"
    ranked = generator.rank_context(sample_documents, query)

    assert len(ranked) == len(sample_documents)
    assert ranked[0].get("context_score", 0) >= ranked[-1].get("context_score", 0)

def test_select_relevant_docs(generator, sample_documents):
    query = "Python"
    selected = generator.select_relevant_docs(sample_documents, query, max_count=1)

    assert len(selected) <= 1

def test_synthesize_response(generator, sample_documents):
    query = "Python"
    context = generator.synthesize_response(query, sample_documents)

    assert len(context) > 0

def test_extract_citations(generator, sample_documents):
    answer = "Python is a programming language"
    citations = generator.extract_citations(answer, sample_documents)

    assert isinstance(citations, list)

def test_validate_answer(generator, sample_documents):
    answer = "Python is a programming language used for data science and machine learning."
    query = "What is Python?"

    is_valid, score, issues = generator.validate_answer(answer, query, sample_documents)

    assert isinstance(is_valid, bool)
    assert 0 <= score <= 1

def test_create_empty_answer(generator):
    answer = generator._create_empty_answer("test query")

    assert isinstance(answer, GeneratedAnswer)
    assert answer.confidence_score == 0.0
    assert len(answer.citations) == 0

def test_format_answer_with_citations(generator, sample_documents):
    with patch.object(generator, '_call_llm', return_value="Test answer"):
        result = generator.generate("test", sample_documents)
        formatted = generator.format_answer_with_citations(result)

        assert len(formatted) > 0

def test_get_quality_report(generator, sample_documents):
    with patch.object(generator, '_call_llm', return_value="Python is a programming language."):
        result = generator.generate("What is Python?", sample_documents)
        report = generator.get_quality_report(result)

        assert "overall_confidence" in report
        assert "validation_score" in report
        assert "quality_breakdown" in report

def test_generate_with_mock_llm(generator, sample_documents):
    with patch.object(generator, '_call_llm', return_value="Python is a programming language."):
        result = generator.generate("What is Python?", sample_documents)

        assert isinstance(result, GeneratedAnswer)
        assert result.query == "What is Python?"
        assert len(result.answer) > 0

def test_generate_empty_documents(generator):
    result = generator.generate("test", [])

    assert isinstance(result, GeneratedAnswer)
    assert result.confidence_score == 0.0
