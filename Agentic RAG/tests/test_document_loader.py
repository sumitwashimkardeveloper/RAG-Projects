import pytest
from pathlib import Path
from modules.utils import TextFileLoader, JSONLoader, DirectoryLoader

@pytest.fixture
def sample_text_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("This is sample content.\nSecond line of content.")
    return str(file_path)

@pytest.fixture
def sample_json_file(tmp_path):
    import json
    file_path = tmp_path / "sample.json"
    data = [
        {"content": "First document", "title": "Doc 1"},
        {"content": "Second document", "title": "Doc 2"}
    ]
    file_path.write_text(json.dumps(data))
    return str(file_path)

def test_text_file_loader(sample_text_file):
    loader = TextFileLoader()
    documents = loader.load(sample_text_file)

    assert len(documents) == 1
    assert "sample content" in documents[0]["content"]
    assert documents[0]["metadata"]["file_type"] == "text"

def test_json_loader(sample_json_file):
    loader = JSONLoader()
    documents = loader.load(sample_json_file)

    assert len(documents) >= 1
    assert documents[0]["metadata"]["file_type"] == "json"

def test_text_loader_nonexistent_file():
    loader = TextFileLoader()
    documents = loader.load("/nonexistent/file.txt")

    assert len(documents) == 0

def test_directory_loader(tmp_path):
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Test content")

    loader = DirectoryLoader()
    documents = loader.load(str(tmp_path))

    assert len(documents) >= 1
