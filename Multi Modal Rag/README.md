# Multi-Modal RAG System

A comprehensive Retrieval Augmented Generation (RAG) system that indexes and retrieves information from multiple media types: Images, Tables, Charts, Videos, Audio, and PowerPoint presentations.

## Features

- **Multi-Modal Support**: Index and retrieve from 6+ media types
- **Smart Chunking**: Automatic content chunking with overlap support
- **Vector Embeddings**: Sentence-Transformer based embeddings
- **Hybrid Search**: Semantic search with media type filtering
- **Context Expansion**: Retrieve related chunks for better context
- **LLM Integration**: LangChain support for answer generation
- **Cross-Modal Analysis**: Find relationships across different media types
- **Performance Reports**: Detailed indexing and retrieval statistics
- **Local & Pinecone**: Works with local vector storage or Pinecone cloud

## Supported Media Types

- **Images**: `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp` (with OCR and object detection)
- **Videos**: `.mp4`, `.avi`, `.mov`, `.mkv` (with frame extraction and transcription)
- **Audio**: `.mp3`, `.wav`, `.flac`, `.aac` (with transcription and feature extraction)
- **Tables**: `.csv`, `.xlsx` (structured data extraction)
- **Charts**: `.jpg`, `.png`, etc. (text and data extraction)
- **PowerPoint**: `.pptx` (slide and notes extraction)
- **Documents**: `.pdf`, `.docx` (text extraction)

## Project Structure

```
multi_modal_rag/
├── config.py                 # Configuration settings
├── media_processors.py       # Media type handlers
├── vector_store.py          # Vector database and embeddings
├── indexer.py               # Indexing pipeline
├── retriever.py             # Retrieval logic
├── rag_pipeline.py          # End-to-end RAG pipeline
├── utils.py                 # Utility functions
├── main.py                  # Basic example
├── advanced_example.py      # Advanced demonstration
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Installation

```bash
pip install -r requirements.txt
```

### Optional Dependencies

For full functionality, install optional dependencies:
- **Tesseract OCR**: For image text extraction
- **Pinecone**: `pip install pinecone-client`
- **OpenAI**: `pip install openai` for LLM integration

## Quick Start

### Basic Indexing

```python
from indexer import MultiModalIndexer

indexer = MultiModalIndexer(use_pinecone=False)
result = indexer.index_directory("./media_folder")
```

### Basic Retrieval

```python
from retriever import MultiModalRetriever

retriever = MultiModalRetriever(vector_store=indexer.vector_store)
results = retriever.retrieve("your query", top_k=5)
```

### Using RAG Pipeline

```python
from rag_pipeline import MultiModalRAGPipeline

pipeline = MultiModalRAGPipeline(use_llm=True)
pipeline.index_directory("./media_folder")

answer = pipeline.query("What is in the documents?")
```

## Configuration

Edit `config.py` to customize:

- **Embedding Model**: Change `EMBEDDING_MODEL` (default: all-MiniLM-L6-v2)
- **Chunk Size**: Adjust `CHUNK_SIZE` for content splitting
- **Pinecone**: Set API keys and index name
- **Media Processors**: Enable/disable specific media type processing

## Examples

### Example 1: Basic Query

```python
from rag_pipeline import MultiModalRAGPipeline

pipeline = MultiModalRAGPipeline()
pipeline.index_directory("./documents")

result = pipeline.query("What are the main topics?")
print(result['answer'])
```

### Example 2: Media Type Filtering

```python
result = pipeline.query_by_media_type(
    "Show me charts about sales",
    media_type="chart",
    top_k=5
)
```

### Example 3: Summarization

```python
summary = pipeline.summarize("document contents")
print(summary['summary'])
```

### Example 4: Analysis with Context

```python
from retriever import MultiModalRetriever

retriever = MultiModalRetriever(vector_store=pipeline.indexer.vector_store)
context = retriever.retrieve_with_context("search term", context_expansion=2)
```

## API Reference

### MultiModalIndexer

- `index_directory(directory_path)` - Index all files in a directory
- `index_file(file_path)` - Index a single file
- `index_bulk_files(file_paths)` - Index multiple files
- `reindex_file(file_path)` - Re-index a file
- `remove_file(file_path)` - Remove indexed file
- `get_indexed_files()` - List indexed files
- `get_indexing_statistics()` - Get statistics

### MultiModalRetriever

- `retrieve(query, top_k, media_type_filter)` - Semantic search
- `retrieve_by_media_type(query, media_type)` - Filter by media type
- `retrieve_with_context(query, context_expansion)` - Get contextual chunks
- `retrieve_multi_media_summary(query)` - Summary by media type
- `retrieve_by_file(file_path, query)` - Search within a file
- `retrieve_cross_modal_relationships(query)` - Find cross-media connections

### MultiModalRAGPipeline

- `index_files(file_paths)` - Index files
- `index_directory(directory_path)` - Index directory
- `query(question, top_k, media_type_filter)` - Ask a question
- `query_by_media_type(question, media_type)` - Filter by type
- `summarize(query)` - Summarize content
- `analyze(query)` - Analyze content
- `compare(query)` - Compare information

## Performance

- Embedding generation: ~100ms per chunk
- Local similarity search: ~50ms for 1000 documents
- Pinecone search: ~100ms (plus network latency)

## Storage

- Local: Documents stored in Python dictionaries (in-memory)
- Pinecone: Cloud-based vector storage
- Metadata: Exported as JSON files

## Integration with LLMs

The system integrates with LangChain and supports:
- OpenAI GPT models
- Custom LLM implementations
- Prompt templates for QA, summarization, analysis

Set `OPENAI_API_KEY` environment variable to enable LLM features.

## Utilities

The `utils.py` module provides:

- **FileUtils**: Directory scanning, file validation, size checking
- **TextUtils**: Text processing, truncation, token estimation
- **PerformanceUtils**: Performance metrics and estimations
- **ReportGenerator**: Generate reports in JSON format
- **ValidationUtils**: Validate files and directories

## Reports Generated

1. **Indexing Report**: Files indexed, chunks created, media type distribution
2. **Retrieval Report**: Query results, confidence scores, retrieval statistics
3. **Health Report**: Vector store status, configuration details
4. **Pipeline Config**: Embeddings, supported formats, LLM status

## Troubleshooting

**Pinecone Connection Failed**: Use local mode or check API keys
**LLM Not Available**: Ensure OpenAI key is set or use pipeline without LLM
**Unsupported File Type**: Check SUPPORTED_*_FORMATS in config.py
**OCR Not Working**: Install Tesseract and set TESSERACT_PATH if needed

## License

MIT License

