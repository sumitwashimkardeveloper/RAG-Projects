import pytest
from unittest.mock import Mock, patch, MagicMock
from app.embeddings.base import BaseEmbeddingProvider, BaseVectorStore
from app.embeddings.tokenizer import TokenCounter


class MockEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self):
        super().__init__("test-model", dimensions=512)

    def embed_text(self, text: str):
        return [0.1] * self.dimensions

    def embed_texts(self, texts):
        return [[0.1] * self.dimensions for _ in texts]


class TestEmbeddingProvider:

    def test_text_hash(self):
        provider = MockEmbeddingProvider()
        hash1 = provider.get_text_hash("hello world")
        hash2 = provider.get_text_hash("hello world")
        assert hash1 == hash2

        hash3 = provider.get_text_hash("different text")
        assert hash1 != hash3

    def test_validate_embedding_valid(self):
        provider = MockEmbeddingProvider()
        embedding = [0.1] * 512
        assert provider.validate_embedding(embedding) is True

    def test_validate_embedding_wrong_dimensions(self):
        provider = MockEmbeddingProvider()
        embedding = [0.1] * 256
        assert provider.validate_embedding(embedding) is False

    def test_validate_embedding_wrong_type(self):
        provider = MockEmbeddingProvider()
        assert provider.validate_embedding("not a list") is False
        assert provider.validate_embedding(None) is False

    def test_embed_text(self):
        provider = MockEmbeddingProvider()
        embedding = provider.embed_text("test text")
        assert len(embedding) == 512
        assert all(isinstance(x, float) for x in embedding)

    def test_embed_texts(self):
        provider = MockEmbeddingProvider()
        texts = ["text1", "text2", "text3"]
        embeddings = provider.embed_texts(texts)
        assert len(embeddings) == 3
        assert all(len(e) == 512 for e in embeddings)


class TestVectorStore:

    def test_vector_store_interface(self):
        class TestStore(BaseVectorStore):
            def connect(self):
                return True

            def index_vector(self, vector_id, vector, metadata=None):
                return True

            def index_vectors(self, vectors):
                return True

            def search(self, query_vector, top_k=10):
                return []

            def delete_vector(self, vector_id):
                return True

            def delete_vectors(self, vector_ids):
                return True

            def get_vector_count(self):
                return 0

        store = TestStore({})
        assert store.connect() is True
        assert store.index_vector("id1", [0.1, 0.2]) is True


class TestTokenCounter:

    def test_count_tokens(self):
        text = "This is a test"
        tokens = TokenCounter.count_tokens(text)
        assert tokens > 0

    def test_count_words(self):
        text = "one two three four"
        words = TokenCounter.count_words(text)
        assert words == 4

    def test_count_sentences(self):
        text = "First. Second. Third."
        sentences = TokenCounter.count_sentences(text)
        assert sentences >= 3

    def test_different_models(self):
        text = "test text for embedding"
        gpt4_tokens = TokenCounter.count_tokens(text, model="gpt-4")
        claude_tokens = TokenCounter.count_tokens(text, model="claude-3-opus")
        assert gpt4_tokens > 0
        assert claude_tokens > 0
