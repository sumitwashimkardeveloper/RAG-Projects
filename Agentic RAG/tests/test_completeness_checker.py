import pytest
from modules.critic import CompletenessChecker

@pytest.fixture
def checker():
    return CompletenessChecker()

@pytest.fixture
def comprehensive_documents():
    return [
        {
            "metadata": {
                "content": "Python is a high-level programming language with dynamic typing and automatic memory management. Created in 1991, it has become one of the most popular programming languages for various applications.",
                "source": "source1"
            }
        },
        {
            "metadata": {
                "content": "Python is extensively used in data science, machine learning, web development, and scientific computing. Libraries like NumPy, Pandas, and TensorFlow make it ideal for data analysis.",
                "source": "source2"
            }
        },
        {
            "metadata": {
                "content": "The Python ecosystem includes package managers like pip and virtual environments for dependency management. The community is very active with regular updates and new libraries.",
                "source": "source3"
            }
        }
    ]

@pytest.fixture
def sparse_documents():
    return [
        {
            "metadata": {
                "content": "Python",
                "source": "source1"
            }
        }
    ]

def test_check_comprehensive(checker, comprehensive_documents):
    query = "What is Python and how is it used?"
    is_complete, score = checker.check(query, comprehensive_documents)

    assert score >= 0.5

def test_check_sparse(checker, sparse_documents):
    query = "What is Python?"
    is_complete, score = checker.check(query, sparse_documents)

    assert score < 0.7

def test_document_count_score(checker):
    assert checker._document_count_score(0) == 0.0
    assert checker._document_count_score(1) < 0.5
    assert checker._document_count_score(5) > 0.7
    assert checker._document_count_score(10) == 1.0

def test_content_quality_score(checker, comprehensive_documents):
    score = checker._content_quality_score(comprehensive_documents)

    assert 0 <= score <= 1

def test_query_coverage_score(checker, comprehensive_documents):
    query = "Python programming language"
    score = checker._query_coverage_score(query, comprehensive_documents)

    assert score > 0

def test_diversity_score(checker, comprehensive_documents):
    score = checker._diversity_score(comprehensive_documents)

    assert score > 0

def test_get_completeness_report(checker, comprehensive_documents):
    query = "What is Python?"
    report = checker.get_completeness_report(query, comprehensive_documents)

    assert "is_complete" in report
    assert "completeness_score" in report
    assert "document_count" in report
    assert "suggestions" in report

def test_needs_more_info(checker, sparse_documents):
    query = "What is Python used for?"
    needs_more = checker.needs_more_info(query, sparse_documents)

    assert isinstance(needs_more, bool)

def test_is_satisfactory(checker, comprehensive_documents):
    query = "Tell me about Python"
    satisfactory = checker.is_satisfactory(query, comprehensive_documents, threshold=0.5)

    assert isinstance(satisfactory, bool)

def test_generate_suggestions_low_completeness(checker):
    query = "test"
    documents = [{"metadata": {"content": "short"}}]

    suggestions = checker._generate_suggestions(False, 0.3, 1, 0.2)

    assert len(suggestions) > 0
    assert any("reformulating" in s.lower() or "increase" in s.lower() for s in suggestions)
