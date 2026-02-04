import pytest
from modules.utils import TextChunker

@pytest.fixture
def chunker():
    return TextChunker(chunk_size=5, overlap=2)

@pytest.fixture
def sample_text():
    return "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10"

def test_chunker_basic(chunker, sample_text):
    chunks = chunker.chunk_text(sample_text, source="test.txt")

    assert len(chunks) > 0
    assert all(chunk.source == "test.txt" for chunk in chunks)

def test_chunker_with_metadata(chunker, sample_text):
    metadata = {"category": "test", "author": "user"}
    chunks = chunker.chunk_text(sample_text, source="test.txt", metadata=metadata)

    assert all("category" in chunk.metadata for chunk in chunks)

def test_chunker_documents():
    chunker = TextChunker(chunk_size=3, overlap=1)
    documents = [
        {"content": "doc1 content here", "source": "file1.txt"},
        {"content": "doc2 more content", "source": "file2.txt"}
    ]

    chunks = chunker.chunk_documents(documents)

    assert len(chunks) > 0
    assert any(chunk.source == "file1.txt" for chunk in chunks)
    assert any(chunk.source == "file2.txt" for chunk in chunks)

def test_chunk_overlap(chunker, sample_text):
    chunks = chunker.chunk_text(sample_text, source="test.txt")

    if len(chunks) > 1:
        chunk_contents = [chunk.content.split() for chunk in chunks]
        for i in range(len(chunk_contents) - 1):
            overlap_words = set(chunk_contents[i][-2:]) & set(chunk_contents[i+1][:2])
            assert len(overlap_words) > 0 or len(chunk_contents[i]) <= 2
