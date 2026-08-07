# Enterprise Knowledge RAG

A production-grade **Retrieval Augmented Generation** system designed for large-scale enterprise knowledge management. It aggregates information from multiple data sources and provides intelligent, contextual answers with complete source attribution.

## Key Features

🏢 **Multi-Source Integration** - Connect PDFs, Confluence, SharePoint, Notion, Google Drive, APIs  
🔗 **Real-time Sync** - Automatic incremental updates from all sources  
🎯 **Semantic Search** - Advanced understanding beyond keyword matching  
📊 **Hybrid Search** - Combine vector similarity with BM25 ranking  
🏆 **Source Attribution** - Know exactly where answers come from  
⚡ **Production Scale** - Handle millions of documents efficiently  
🔐 **Enterprise Security** - Access controls, audit logs, data encryption  

## Architecture

```
Data Sources
├── Confluence
├── SharePoint
├── Notion
├── Google Drive
├── Email Archives
├── REST APIs
└── Web Content
    ↓
[Data Ingestion Pipeline]
├── Document Parser
├── API Connectors
├── Batch Processor
└── Change Detection
    ↓
[Text Processing]
├── Extraction & Cleaning
├── Semantic Chunking
├── Normalization
└── Quality Assurance
    ↓
[Vector Embeddings]
├── OpenAI/Anthropic Embeddings
├── Batch Processing
├── Caching Layer
└── Vector Database (Pinecone/Weaviate)
    ↓
[Multi-Stage Retrieval]
├── Vector Search
├── BM25 Ranking
├── Re-ranking
└── Diversity Optimization
    ↓
[LLM Answer Generation]
├── Prompt Engineering
├── Context Assembly
├── Source Attribution
└── Confidence Scoring
    ↓
User-Facing API
└── Citation & Metadata
```

## Installation

### Prerequisites

```
Python 3.10+
Node.js 18+ (optional, for TypeScript)
PostgreSQL 14+ (metadata storage)
Redis 7+ (caching)
Docker & Docker Compose
```

### Core Dependencies

```
Backend Framework: FastAPI / Flask
LLM Orchestration: LangChain
Vector Database: Pinecone / Weaviate / Milvus
Document Parsing: python-docx, PyPDF2, python-pptx
Indexing: LlamaIndex
Data Validation: Pydantic
```

### Setup

1. **Create environment file:**
```bash
cp .env.example .env
```

2. **Configure credentials:**
```env
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Vector Database
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west4-gcp-free

# Data Source Connectors
CONFLUENCE_URL=https://company.atlassian.net
CONFLUENCE_TOKEN=...
SHAREPOINT_CLIENT_ID=...
SHAREPOINT_CLIENT_SECRET=...
NOTION_API_KEY=...

# Database
POSTGRES_URL=postgresql://user:pass@localhost/rag_db
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Initialize databases:**
```bash
python setup_db.py
```

## Quick Start

### 1. Data Ingestion

```python
from ingestion.pipeline import DataIngestionPipeline

pipeline = DataIngestionPipeline()

# Add data sources
pipeline.add_confluence_source("https://company.atlassian.net", token="...")
pipeline.add_sharepoint_source("https://company.sharepoint.com", client_id="...")
pipeline.add_drive_source("https://drive.google.com", credentials="...")

# Ingest all sources
results = pipeline.run_full_sync()
print(f"Documents ingested: {results['total_documents']}")
print(f"Chunks created: {results['total_chunks']}")
```

### 2. Process Documents

```python
from processing.text_processor import TextProcessor

processor = TextProcessor(
    chunk_size=1024,
    chunk_overlap=256,
    min_chunk_size=100
)

# Process and validate
processed = processor.process_documents(documents)
print(f"Quality score: {processed['quality_metrics']['avg_score']}")
```

### 3. Embed & Store

```python
from vectorization.embedding_service import EmbeddingService
from vectorization.vector_store import VectorStore

embedder = EmbeddingService(provider="openai", model="text-embedding-3-large")
vector_store = VectorStore(provider="pinecone")

# Generate embeddings
embeddings = embedder.embed_batch(chunks, batch_size=100)

# Store in vector DB
vector_store.upsert(embeddings, metadata=metadata)
```

### 4. Query the System

```python
from retrieval.rag_system import RAGSystem

rag = RAGSystem()

# Query with multiple stages
result = rag.query(
    "How do we handle data retention policies?",
    top_k=5,
    use_reranker=True,
    filter_by_source=["confluence", "sharepoint"]
)

print(f"Answer: {result['answer']}")
print(f"Sources:")
for citation in result['citations']:
    print(f"  - {citation['source']}: {citation['snippet']}")
print(f"Confidence: {result['confidence']:.1%}")
```

## API Usage

### Start Server

```bash
python main.py
# Server: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Query Endpoint

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is our remote work policy?",
    "top_k": 5,
    "filters": {
      "sources": ["confluence"],
      "date_range": "last_30_days"
    }
  }'
```

### Response Example

```json
{
  "query": "What is our remote work policy?",
  "answer": "Our company...",
  "documents": [
    {
      "id": "doc_123",
      "title": "Company Policies - Remote Work",
      "source": "confluence",
      "url": "https://...",
      "score": 0.94,
      "excerpt": "..."
    }
  ],
  "citations": [
    {
      "source": "confluence",
      "snippet": "Employees are allowed to work...",
      "relevance_score": 0.94,
      "document_id": "doc_123"
    }
  ],
  "confidence": 0.91,
  "processing_time_ms": 1250
}
```

## Core Components

### Data Ingestion (`ingestion/`)

| Component | Purpose |
|-----------|---------|
| `document_parser.py` | Parse PDFs, Word docs, Excel files |
| `api_connectors/` | Confluence, SharePoint, Notion, Google Drive |
| `batch_service.py` | Queue-based processing with Celery |
| `change_detector.py` | Monitor source updates for sync |

### Text Processing (`processing/`)

| Component | Purpose |
|-----------|---------|
| `text_processor.py` | Extraction, cleaning, normalization |
| `chunker.py` | Semantic & fixed-size chunking |
| `quality_validator.py` | Duplicate detection, quality scoring |

### Vectorization (`vectorization/`)

| Component | Purpose |
|-----------|---------|
| `embedding_service.py` | OpenAI/Anthropic embeddings with caching |
| `vector_store.py` | Pinecone/Weaviate/Milvus interface |
| `index_manager.py` | Index versioning, maintenance |

### Retrieval (`retrieval/`)

| Component | Purpose |
|-----------|---------|
| `multi_stage_retriever.py` | Vector + BM25 hybrid search |
| `reranker.py` | Cross-encoder re-ranking |
| `context_assembler.py` | Build optimal context windows |
| `cache_layer.py` | Query result caching |

### LLM Integration (`llm/`)

| Component | Purpose |
|-----------|---------|
| `prompt_manager.py` | Prompt templates & engineering |
| `llm_orchestrator.py` | Model selection & fallbacks |
| `response_generator.py` | Answer generation with streaming |
| `citation_engine.py` | Source attribution |

## Configuration

### Main Config (`config.yaml`)

```yaml
# Data Processing
ingestion:
  chunk_size: 1024
  chunk_overlap: 256
  min_chunk_size: 100
  quality_threshold: 0.6

# Vector Database
vector_db:
  provider: pinecone
  index_name: enterprise-knowledge
  dimension: 1536
  metric: cosine

# Retrieval Settings
retrieval:
  top_k_initial: 20
  top_k_final: 5
  use_bm25: true
  use_reranker: true
  similarity_threshold: 0.5

# LLM Configuration
llm:
  provider: openai
  model: gpt-4-turbo-preview
  temperature: 0.3
  max_tokens: 2048

# Caching
cache:
  enabled: true
  ttl_seconds: 3600
  max_queries: 10000

# Monitoring
monitoring:
  log_level: INFO
  track_metrics: true
  alert_on_errors: true
```

## Monitoring & Observability

### Key Metrics

```yaml
Ingestion:
  - Documents processed per hour
  - Chunk quality scores
  - Source sync latency

Retrieval:
  - Query latency (p50, p95, p99)
  - Retrieval quality (MRR, NDCG)
  - Cache hit rate

Answer Quality:
  - LLM model latency
  - Token usage and costs
  - Confidence scores
  - User satisfaction ratings
```

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "components": {
    "vector_db": "connected",
    "postgres": "connected",
    "redis": "connected",
    "llm_provider": "available"
  },
  "metrics": {
    "indexed_documents": 45230,
    "avg_query_latency_ms": 1200
  }
}
```

## Development Workflow

### Implementation Phases

**Phase 1: Setup & Dependencies**
- Environment configuration
- Dependency installation
- Database initialization

**Phase 2: Data Ingestion**
- Build document parsers
- Implement API connectors
- Create batch processor

**Phase 3: Text Processing**
- Text extraction & cleaning
- Semantic chunking strategy
- Quality validation

**Phase 4: Vector Embeddings**
- Embedding service
- Vector DB setup
- Index optimization

**Phase 5: Retrieval & Ranking**
- Multi-stage retrieval
- Re-ranking with cross-encoders
- Context optimization

**Phase 6: LLM Integration**
- Prompt engineering
- Response generation
- Citation handling

**Phase 7: API & Deployment**
- REST API endpoints
- Docker containers
- Kubernetes manifests

## Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/rag
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7

volumes:
  postgres_data:
```

### Deploy to Kubernetes

```bash
# Build and push image
docker build -t company/enterprise-rag:latest .
docker push company/enterprise-rag:latest

# Deploy
kubectl apply -f k8s/

# Verify
kubectl get pods -l app=enterprise-rag
```

### Production Checklist

- [ ] Environment variables secured with vault
- [ ] Database backups configured
- [ ] Monitoring & alerting set up
- [ ] Rate limiting enabled
- [ ] Request logging configured
- [ ] API authentication implemented
- [ ] SSL/TLS certificates installed
- [ ] Load balancer configured
- [ ] Auto-scaling policies set
- [ ] Disaster recovery plan

## Performance Tuning

### Query Optimization

```python
# Optimize similarity threshold
retriever.set_similarity_threshold(0.6)

# Reduce initial candidates for speed
retriever.set_top_k_initial(10)  # default 20

# Use BM25 for keyword-heavy queries
retriever.use_keyword_search(True)
```

### Cost Optimization

```python
# Cache frequent queries
cache.enable_for_popular_queries(top_n=1000)

# Batch embeddings
embedder.batch_size = 100

# Use cheaper embedding model
embedder.model = "text-embedding-3-small"
```

## Troubleshooting

### Data Ingestion Issues

```bash
# Check source connectivity
python -c "from ingestion import test_source; test_source('confluence')"

# Verify API credentials
python ingestion/connectors/confluence_connector.py test

# Monitor ingestion progress
tail -f logs/ingestion.log | grep -E "ERROR|WARNING"
```

### Query Performance

```bash
# Profile retrieval latency
python -m cProfile -s cumtime main.py

# Check vector DB stats
python -c "print(vector_store.get_index_stats())"

# Analyze slow queries
SELECT query, latency_ms FROM query_log WHERE latency_ms > 3000
```

### Memory Issues

```bash
# Reduce batch size
config.set("ingestion.batch_size", 10)

# Clear cache
python -c "import redis; r = redis.Redis(); r.flushdb()"

# Check memory usage
docker stats enterprise-rag-api
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## Testing

```bash
# Run all tests
pytest tests/

# With coverage
pytest --cov=src tests/

# Specific module
pytest tests/test_retriever.py -v

# Integration tests
pytest tests/integration/ -v --duration=10
```

## License

MIT License - See LICENSE file for details

## Support

- **Documentation**: See docs/ directory
- **Issues**: GitHub Issues
- **Contact**: enterprise-rag@company.com
