# Multi-Modal RAG System

A comprehensive **Retrieval Augmented Generation** system that indexes and retrieves information from **6+ media types**: Images (with OCR), Videos (with frame extraction), Audio (with transcription), Tables, Charts, Documents, and PowerPoint presentations.

## Key Features

🎬 **Multi-Modal Support** - Index images, videos, audio, tables, charts, PDFs, PowerPoint  
🔍 **Smart Extraction** - OCR for images, transcription for audio/video, parsing for tables  
🧠 **Intelligent Chunking** - Automatic content splitting with configurable overlap  
📊 **Semantic Search** - Vector embeddings with Sentence-Transformer  
🎯 **Hybrid Search** - Semantic search combined with media type filtering  
🔗 **Cross-Modal Analysis** - Find relationships across different media types  
📈 **Performance Reports** - Detailed indexing and retrieval statistics  
☁️ **Flexible Storage** - Local in-memory or cloud-based Pinecone  

## Supported Media Types

| Format | Extensions | Extraction Method |
|--------|-----------|------------------|
| **Images** | .jpg, .jpeg, .png, .webp, .bmp | OCR + object detection |
| **Videos** | .mp4, .avi, .mov, .mkv | Frame extraction + transcription |
| **Audio** | .mp3, .wav, .flac, .aac | Speech-to-text transcription |
| **Tables** | .csv, .xlsx | Structured data parsing |
| **Charts** | .jpg, .png, .pdf | Text extraction + data recognition |
| **PowerPoint** | .pptx | Slide + notes extraction |
| **Documents** | .pdf, .docx, .txt | Text extraction |

## Architecture

```
Media Files
├── Images
├── Videos
├── Audio
├── Tables
├── Charts
├── PowerPoint
└── Documents
    ↓
[Media Type Detection]
    - File type identification
    - Format validation
    ↓
[Content Extraction]
    ├── Images: OCR, object detection
    ├── Video: Frame extraction, transcription
    ├── Audio: Speech-to-text
    ├── Tables: Structured parsing
    ├── Charts: Data extraction
    ├── PowerPoint: Slide parsing
    └── Docs: Text extraction
    ↓
[Smart Chunking]
    - Media-type-specific splitting
    - Metadata preservation
    - Overlap configuration
    ↓
[Embedding Generation]
    - Sentence-Transformer embeddings
    - Batch processing
    ↓
[Vector Storage]
    └── Local memory or Pinecone cloud
    ↓
[Retrieval Pipeline]
    ├── Semantic search
    ├── Media type filtering
    ├── Context expansion
    └── Cross-modal linking
    ↓
[LLM Integration]
    - Answer generation
    - Summarization
    - Analysis
    ↓
User Response
```

## Installation

### Prerequisites

```
Python 3.9+
FFmpeg (for video/audio processing)
Tesseract OCR (for image text extraction)
```

### Optional Dependencies

For full functionality, install optional packages:

```bash
# Image processing
pip install pdf2image pillow pytesseract

# Video/Audio processing  
pip install moviepy librosa

# Cloud storage
pip install pinecone-client

# LLM integration
pip install openai langchain
```

### Quick Setup

1. **Install core dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install FFmpeg:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (via conda)
conda install ffmpeg -c conda-forge
```

3. **Install Tesseract OCR:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows - Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Quick Start

### 1. Basic Indexing

```python
from indexer import MultiModalIndexer

# Initialize indexer
indexer = MultiModalIndexer(use_pinecone=False)

# Index directory
result = indexer.index_directory("./media_folder")

print(f"Indexed: {result['files_processed']} files")
print(f"Chunks created: {result['total_chunks']}")
print(f"Embedding time: {result['embedding_time_ms']}ms")
```

### 2. Basic Retrieval

```python
from retriever import MultiModalRetriever

# Initialize retriever
retriever = MultiModalRetriever(vector_store=indexer.vector_store)

# Semantic search
results = retriever.retrieve("your query", top_k=5)

for result in results:
    print(f"Source: {result['source']}")
    print(f"Score: {result['score']:.2f}")
    print(f"Content: {result['text'][:100]}...")
```

### 3. Using RAG Pipeline

```python
from rag_pipeline import MultiModalRAGPipeline

# Initialize with LLM
pipeline = MultiModalRAGPipeline(use_llm=True)

# Index directory
pipeline.index_directory("./media_folder")

# Query with answer generation
answer = pipeline.query("What is in the documents?")
print(f"Answer: {answer['answer']}")
print(f"Sources: {answer['sources']}")
```

## Core Components

### MultiModalIndexer

Handles document ingestion and embedding:

```python
from indexer import MultiModalIndexer

indexer = MultiModalIndexer(
    use_pinecone=False,
    embedding_model="all-MiniLM-L6-v2",
    chunk_size=512,
    chunk_overlap=100
)

# Index operations
indexer.index_directory("./documents/")
indexer.index_file("document.pdf")
indexer.index_bulk_files(["file1.pdf", "file2.pptx"])

# Management
files = indexer.get_indexed_files()
stats = indexer.get_indexing_statistics()
```

### MultiModalRetriever

Performs semantic and filtered search:

```python
from retriever import MultiModalRetriever

retriever = MultiModalRetriever(vector_store=indexer.vector_store)

# Semantic search
results = retriever.retrieve("search term", top_k=5)

# Filter by media type
images = retriever.retrieve_by_media_type("objects", media_type="image")
charts = retriever.retrieve_by_media_type("sales data", media_type="chart")

# Context expansion
results = retriever.retrieve_with_context("query", context_expansion=2)

# Cross-modal relationships
relationships = retriever.retrieve_cross_modal_relationships("query")
```

### MultiModalRAGPipeline

End-to-end RAG with LLM integration:

```python
from rag_pipeline import MultiModalRAGPipeline

pipeline = MultiModalRAGPipeline(
    use_llm=True,
    llm_provider="openai",
    model="gpt-4"
)

# Indexing
pipeline.index_files(["doc1.pdf", "doc2.pptx"])
pipeline.index_directory("./media/")

# Querying
answer = pipeline.query("Question about documents?", top_k=5)
summary = pipeline.summarize("Document content")
analysis = pipeline.analyze("Analyze this content")
comparison = pipeline.compare("Compare X and Y")
```

## API Reference

### Indexer Methods

| Method | Description |
|--------|-------------|
| `index_directory(path)` | Index all files in directory |
| `index_file(path)` | Index single file |
| `index_bulk_files(paths)` | Index multiple files |
| `reindex_file(path)` | Re-index existing file |
| `remove_file(path)` | Remove indexed file |
| `get_indexed_files()` | List all indexed files |
| `get_indexing_statistics()` | Retrieve statistics |

### Retriever Methods

| Method | Description |
|--------|-------------|
| `retrieve(query, top_k)` | Semantic search |
| `retrieve_by_media_type(query, media_type)` | Filter by type |
| `retrieve_with_context(query, context_expansion)` | Get contextual chunks |
| `retrieve_multi_media_summary(query)` | Summary by media type |
| `retrieve_by_file(file_path, query)` | Search within file |
| `retrieve_cross_modal_relationships(query)` | Find cross-media connections |

### Pipeline Methods

| Method | Description |
|--------|-------------|
| `index_files(paths)` | Index files |
| `index_directory(path)` | Index directory |
| `query(question, top_k, filter)` | Ask question |
| `query_by_media_type(question, media_type)` | Query specific type |
| `summarize(content)` | Generate summary |
| `analyze(content)` | Analyze content |
| `compare(content)` | Compare information |

## Configuration

Edit `config.py` to customize behavior:

```python
# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence-Transformer model
EMBEDDING_DIMENSION = 384

# Chunking Strategy
CHUNK_SIZE = 512                       # Characters per chunk
CHUNK_OVERLAP = 100                    # Overlap between chunks
MIN_CHUNK_SIZE = 50                    # Minimum chunk size

# Supported Formats
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.flac', '.aac']
SUPPORTED_TABLE_FORMATS = ['.csv', '.xlsx']
SUPPORTED_DOC_FORMATS = ['.pdf', '.docx', '.txt']
SUPPORTED_PPTX_FORMATS = ['.pptx']

# Media Processors
ENABLE_IMAGE_PROCESSING = True
ENABLE_VIDEO_PROCESSING = True
ENABLE_AUDIO_PROCESSING = True
ENABLE_OCR = True                      # Image text extraction
ENABLE_VIDEO_TRANSCRIPTION = True      # Video-to-text

# Pinecone Configuration
USE_PINECONE = False
PINECONE_API_KEY = None
PINECONE_ENVIRONMENT = "us-west1-gcp"
PINECONE_INDEX_NAME = "multi-modal-rag"

# LLM Configuration
LLM_PROVIDER = "openai"
OPENAI_API_KEY = None
OPENAI_MODEL = "gpt-4"
ANTHROPIC_API_KEY = None

# Performance
BATCH_SIZE = 32                        # Embedding batch size
MAX_WORKERS = 4                        # Parallel processing threads
TIMEOUT_SECONDS = 300                  # Processing timeout
```

## Usage Examples

### Example 1: Index Mixed Media

```python
from indexer import MultiModalIndexer
from retriever import MultiModalRetriever

# Index a folder with mixed media types
indexer = MultiModalIndexer()
result = indexer.index_directory("./company_docs/")

print(f"Total files: {result['total_files']}")
print(f"Total chunks: {result['total_chunks']}")
print(f"Chunks by type:")
for media_type, count in result['chunks_by_media_type'].items():
    print(f"  {media_type}: {count}")
```

### Example 2: Media Type Filtering

```python
retriever = MultiModalRetriever(vector_store=indexer.vector_store)

# Get only image results
image_results = retriever.retrieve_by_media_type(
    "product photos",
    media_type="image",
    top_k=5
)

# Get chart data
charts = retriever.retrieve_by_media_type(
    "quarterly sales",
    media_type="chart"
)

# Get from presentations
slides = retriever.retrieve_by_media_type(
    "company strategy",
    media_type="powerpoint"
)
```

### Example 3: LLM-Based Summarization

```python
pipeline = MultiModalRAGPipeline(use_llm=True)

# Index documents
pipeline.index_directory("./reports/")

# Summarize content
summary = pipeline.summarize(
    "annual report content",
    max_length=500
)
print(f"Summary: {summary['summary']}")
```

### Example 4: Cross-Modal Analysis

```python
retriever = MultiModalRetriever(vector_store=pipeline.indexer.vector_store)

# Find connections across media types
relationships = retriever.retrieve_cross_modal_relationships(
    "product launch timeline"
)

for rel in relationships:
    print(f"Image mentions {rel['text']} (confidence: {rel['confidence']})")
```

### Example 5: File-Specific Search

```python
# Search within specific file
results = retriever.retrieve_by_file(
    "document.pdf",
    "specific search term",
    top_k=3
)

for result in results:
    print(f"Found in: {result['file_path']}")
    print(f"Content: {result['text']}")
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Embedding generation | ~100ms per chunk | Batch processing faster |
| Local similarity search | ~50ms for 1K docs | Single query |
| Pinecone search | ~100ms | Plus network latency |
| Image OCR | 1-5s per image | Depends on complexity |
| Video frame extraction | 10-30s per minute | Parallel processing |
| Audio transcription | 5-10x realtime | Depends on audio quality |

## Storage Options

### Local Storage

```python
# In-memory vector store
indexer = MultiModalIndexer(use_pinecone=False)

# Metadata exported as JSON
indexer.export_metadata("./metadata.json")
```

Characteristics:
- Fast for small collections (< 10K chunks)
- No API costs
- Data lost on restart
- Single machine only

### Pinecone Cloud

```python
# Cloud-based vector storage
indexer = MultiModalIndexer(
    use_pinecone=True,
    pinecone_api_key="...",
    pinecone_index_name="multi-modal"
)
```

Characteristics:
- Scalable to millions of vectors
- Persistent storage
- Network latency overhead
- API costs

## LLM Integration

Supports multiple LLM providers:

### OpenAI

```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'

pipeline = MultiModalRAGPipeline(
    use_llm=True,
    llm_provider="openai",
    model="gpt-4"
)
```

### Anthropic Claude

```python
import os
os.environ['ANTHROPIC_API_KEY'] = 'sk-...'

pipeline = MultiModalRAGPipeline(
    use_llm=True,
    llm_provider="anthropic",
    model="claude-3-opus"
)
```

### Custom LLM

```python
from rag_pipeline import MultiModalRAGPipeline

pipeline = MultiModalRAGPipeline()
pipeline.llm = custom_llm_instance
```

## Reports & Statistics

### Indexing Report

```python
stats = indexer.get_indexing_statistics()

print(f"Files indexed: {stats['files_indexed']}")
print(f"Total chunks: {stats['total_chunks']}")
print(f"Avg chunk size: {stats['avg_chunk_size']}")
print(f"Processing time: {stats['processing_time_ms']}ms")

# By media type
for media_type, data in stats['by_media_type'].items():
    print(f"{media_type}: {data['chunk_count']} chunks")
```

### Retrieval Report

```python
results = retriever.retrieve("query", top_k=5)

# Results contain:
# - score: similarity score
# - media_type: image, video, audio, etc.
# - source: file path
# - text: extracted content
# - confidence: extraction confidence
```

## Troubleshooting

### FFmpeg Not Found

```bash
# Verify installation
ffmpeg -version

# Set path if needed
import os
os.environ['FFMPEG_PATH'] = '/usr/local/bin/ffmpeg'
```

### Tesseract OCR Issues

```bash
# Verify installation
tesseract --version

# Set path if needed
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Memory Issues

```python
# Reduce batch size
config.BATCH_SIZE = 8

# Process in smaller chunks
indexer.index_directory("./docs", batch_size=5)

# Clear cache
import gc
gc.collect()
```

### Pinecone Connection

```bash
# Test connection
python -c "from pinecone import Pinecone; pc = Pinecone(api_key='...')"

# Verify index exists
python -c "print(pc.Index('index-name').describe_index_stats())"
```

### LLM Not Available

```python
# Ensure API key is set
import os
print(os.environ.get('OPENAI_API_KEY'))

# Use pipeline without LLM
pipeline = MultiModalRAGPipeline(use_llm=False)
```

## Development & Testing

### Run Tests

```bash
pytest tests/ -v

# With coverage
pytest --cov=. tests/

# Specific test
pytest tests/test_indexer.py -v
```

### Code Quality

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## File Structure

```
multi_modal_rag/
├── config.py                 # Configuration
├── media_processors.py       # Media type handlers
├── vector_store.py          # Vector storage interface
├── indexer.py               # Indexing pipeline
├── retriever.py             # Retrieval logic
├── rag_pipeline.py          # End-to-end pipeline
├── utils.py                 # Utility functions
├── main.py                  # Basic example
├── advanced_example.py      # Advanced demo
├── requirements.txt         # Dependencies
│
├── tests/
│   ├── test_indexer.py
│   ├── test_retriever.py
│   └── test_rag_pipeline.py
│
├── examples/
│   ├── index_images.py
│   ├── index_videos.py
│   ├── cross_modal_search.py
│   └── llm_integration.py
│
└── README.md               # This file
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add feature'`
4. Push: `git push origin feature/new-feature`
5. Open Pull Request

## License

MIT License - See LICENSE file for details

## Next Steps

1. Install dependencies and FFmpeg/Tesseract
2. Configure `config.py` for your needs
3. Run `main.py` for basic example
4. Check `advanced_example.py` for advanced usage
5. Review example scripts in `examples/` directory
6. Explore `retriever.py` for advanced retrieval strategies
