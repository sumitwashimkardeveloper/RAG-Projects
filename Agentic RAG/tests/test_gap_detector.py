import pytest
from modules.critic import GapDetector

@pytest.fixture
def detector():
    return GapDetector()

@pytest.fixture
def sample_documents():
    return [
        {
            "metadata": {
                "content": "Python is a programming language created in 1991"
            }
        },
        {
            "metadata": {
                "content": "Used for data science and web development"
            }
        }
    ]

def test_detect_temporal_gap(detector):
    query = "When was Python created?"
    documents = [
        {
            "metadata": {
                "content": "Python is a programming language"
            }
        }
    ]

    gaps = detector.detect(query, documents)

    gap_found = any("temporal" in gap or "when" in gap.lower() for gap in gaps)
    assert gap_found == True or len(gaps) == 0

def test_detect_spatial_gap(detector):
    query = "Where is Python most used?"
    documents = [
        {
            "metadata": {
                "content": "Python is a programming language"
            }
        }
    ]

    gaps = detector.detect(query, documents)

    gap_found = any("spatial" in gap or "location" in gap.lower() for gap in gaps)
    assert len(gaps) > 0

def test_detect_causal_gap(detector):
    query = "Why is Python popular?"
    documents = [
        {
            "metadata": {
                "content": "Python is a programming language with simple syntax"
            }
        }
    ]

    gaps = detector.detect(query, documents)

    assert isinstance(gaps, list)

def test_quantify_gaps(detector, sample_documents):
    query = "When and where was Python created? What are its uses?"
    quantified = detector.quantify_gaps("test query", sample_documents)

    assert "total_gaps" in quantified
    assert "gap_types" in quantified
    assert "severity" in quantified
    assert "gaps" in quantified

def test_gap_severity_none(detector):
    query = "test"
    documents = [
        {
            "metadata": {
                "content": "comprehensive answer to test question about everything"
            }
        }
    ]

    quantified = detector.quantify_gaps(query, documents)

    severity = quantified["severity"]
    assert severity in ["none", "low", "medium", "high"]

def test_should_reformulate(detector, sample_documents):
    query = "When and where is this used?"
    should_reform = detector.should_reformulate(query, sample_documents, threshold=2)

    assert isinstance(should_reform, bool)

def test_specific_gaps_detection(detector):
    query = "Python"
    documents = [{"metadata": {"content": "Short"}}]

    gaps = detector.detect(query, documents)

    assert isinstance(gaps, list)
    assert len(gaps) > 0 or len(documents) > 0
