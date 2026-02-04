import pytest
from modules.utils import AnthropicEmbeddings, OpenAIEmbeddings

@pytest.fixture
def sample_texts():
    return [
        "This is the first sample text.",
        "This is the second sample text.",
        "Another example for testing embeddings."
    ]

def test_anthropic_embeddings():
    try:
        embeddings = AnthropicEmbeddings()
        assert embeddings.dimension == 1536
    except ImportError:
        pytest.skip("anthropic package not installed")

def test_openai_embeddings():
    try:
        embeddings = OpenAIEmbeddings()
        assert embeddings.dimension == 1536
    except ImportError:
        pytest.skip("openai package not installed")

def test_embedding_dimension_consistency(sample_texts):
    try:
        embeddings = OpenAIEmbeddings()
        vectors = embeddings.embed_texts(sample_texts)

        expected_dim = embeddings.dimension
        for vector in vectors:
            assert len(vector) == expected_dim
    except ImportError:
        pytest.skip("openai package not installed")

def test_single_vs_batch_embedding():
    try:
        embeddings = OpenAIEmbeddings()
        text = "Test text for embedding"

        single = embeddings.embed_text(text)
        batch = embeddings.embed_texts([text])

        assert len(single) == len(batch[0])
    except ImportError:
        pytest.skip("openai package not installed")
