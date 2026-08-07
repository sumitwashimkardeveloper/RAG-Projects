# RAG Variants - Retrieval Augmented Generation Systems

A comprehensive repository containing **4 distinct production-grade RAG implementations**, each optimized for different use cases and architectural patterns. Choose the variant that best fits your requirements.

## 🎯 Quick Overview

| Variant | Best For | Key Feature | Complexity |
|---------|----------|------------|-----------|
| **[Agentic RAG](#-agentic-rag)** | Iterative refinement, high accuracy needs | Multi-iteration reasoning loop | 🟠 Medium |
| **[Enterprise RAG](#-enterprise-rag)** | Large organizations, multiple data sources | Multi-source integration, real-time sync | 🔴 High |
| **[Graph RAG](#-graph-rag)** | Relationship-heavy queries, explainability | Neo4j knowledge graphs, entity relationships | 🟠 Medium |
| **[Multi-Modal RAG](#-multi-modal-rag)** | Mixed media content | Images, videos, audio, tables, charts | 🟠 Medium |

## 🤖 Agentic RAG

**Iterative query refinement through multi-stage reasoning loops**

Perfect for scenarios requiring high accuracy where answers benefit from iterative improvement.

### Key Features
- 🔄 Iterative query refinement based on critic feedback
- 🎯 Multi-stage retrieval with automatic query rewriting
- 📊 Confidence scoring and answer validation
- ⚡ Async API with background task support

### Quick Start
```bash
cd "Agentic RAG"
pip install -r requirements.txt
cp .env.template .env
python api.py
# Server: http://localhost:8000
```

### Use Cases
- Complex research questions
- Accuracy-critical applications
- Adaptive query strategies
- Interactive Q&A systems

**[📖 Full Documentation →](Agentic%20RAG/README.md)**

---

## 🏢 Enterprise RAG

**Multi-source enterprise knowledge management at scale**

Ideal for large organizations needing to aggregate information from multiple platforms (Confluence, SharePoint, Notion, Google Drive, etc.).

### Key Features
- 🌐 Multi-source integration (7+ data sources)
- 🔄 Real-time incremental sync
- 🎯 Hybrid search (semantic + BM25 ranking)
- 📊 Advanced retrieval with re-ranking
- 🔐 Enterprise-grade security & audit logs

### Quick Start
```bash
cd "Enterprise RAG"
pip install -r requirements.txt
cp .env.example .env
# Configure your data sources
python main.py
```

### Use Cases
- Enterprise knowledge bases
- Multi-team collaboration
- Data consolidation
- Compliance documentation
- Internal knowledge discovery

**[📖 Full Documentation →](Enterprise%20RAG/README.md)**

---

## 🔗 Graph RAG

**Knowledge graph-based retrieval with relationship reasoning**

Best for applications where understanding relationships between entities is critical.

### Key Features
- 🧠 Neo4j knowledge graph construction
- 🔗 Relationship-aware entity extraction
- 🧭 Graph traversal and path finding
- 📈 Advanced analytics (centrality, communities)
- 📊 Explainable answers through entity paths

### Quick Start
```bash
cd "Graph RAG"
pip install -r requirements.txt
cp .env.example .env
docker-compose up -d neo4j
python init_schema.py
python main.py
```

### Use Cases
- Knowledge base systems
- Citation networks
- Organizational relationships
- Scientific knowledge graphs
- Recommendation systems

**[📖 Full Documentation →](Graph%20RAG/README.md)**

---

## 🎬 Multi-Modal RAG

**Handle 6+ media types in a unified retrieval system**

Perfect for applications working with diverse content: documents, images, videos, audio, tables, charts, and presentations.

### Key Features
- 📸 Image processing with OCR
- 🎥 Video frame extraction & transcription
- 🔊 Audio speech-to-text
- 📊 Table and chart parsing
- 🔗 Cross-modal relationship discovery
- ☁️ Local or cloud storage (Pinecone)

### Quick Start
```bash
cd "Multi Modal RAG"
pip install -r requirements.txt
# Install FFmpeg and Tesseract (see README)
python main.py
```

### Use Cases
- Document analysis platforms
- Research content management
- Media archive search
- Business intelligence
- Knowledge management systems

**[📖 Full Documentation →](Multi%20Modal%20RAG/README.md)**

---

## 📊 Comparison Matrix

### Data Source Support

| Feature | Agentic | Enterprise | Graph | Multi-Modal |
|---------|---------|-----------|-------|------------|
| **PDF Documents** | ✅ | ✅ | ✅ | ✅ |
| **Word Documents** | ✅ | ✅ | ✅ | ✅ |
| **Web APIs** | ✅ | ✅ | ✅ | ✅ |
| **Confluence** | ✅ | ✅ | ✅ | ❌ |
| **SharePoint** | ✅ | ✅ | ✅ | ❌ |
| **Images** | ❌ | ❌ | ❌ | ✅ |
| **Videos** | ❌ | ❌ | ❌ | ✅ |
| **Audio** | ❌ | ❌ | ❌ | ✅ |
| **Databases** | Memory | PostgreSQL | Neo4j | Memory/Pinecone |

### Retrieval Strategies

| Strategy | Agentic | Enterprise | Graph | Multi-Modal |
|----------|---------|-----------|-------|------------|
| **Vector Search** | ✅ | ✅ | ✅ | ✅ |
| **BM25 Ranking** | ✅ | ✅ | ✅ | ❌ |
| **Graph Traversal** | ❌ | ❌ | ✅ | ❌ |
| **Entity Extraction** | ✅ | ✅ | ✅ | ❌ |
| **Multi-Iteration** | ✅ | ❌ | ❌ | ❌ |
| **Media Filtering** | ❌ | ❌ | ❌ | ✅ |

### LLM Integration

| Capability | Agentic | Enterprise | Graph | Multi-Modal |
|-----------|---------|-----------|-------|------------|
| **Answer Generation** | ✅ | ✅ | ✅ | ✅ |
| **Answer Criticism** | ✅ | ❌ | ❌ | ❌ |
| **Streaming** | ✅ | ✅ | ✅ | ✅ |
| **Source Attribution** | ✅ | ✅ | ✅ | ✅ |
| **Summarization** | ✅ | ✅ | ✅ | ✅ |

### Performance Targets

| Metric | Agentic | Enterprise | Graph | Multi-Modal |
|--------|---------|-----------|-------|------------|
| **Query Latency** | 1-3s | < 2s | 0.8-1.5s | < 2s |
| **Throughput** | 100+ QPS | 500+ QPS | 200+ QPS | 100+ QPS |
| **Max Documents** | 100K+ | 1M+ | 500K+ | 100K+ |
| **Concurrent Users** | 50+ | 1000+ | 200+ | 50+ |

---

## 🚀 Getting Started

### Choose Your Variant

1. **Need to refine queries iteratively?** → [Agentic RAG](#-agentic-rag)
2. **Managing enterprise knowledge from multiple sources?** → [Enterprise RAG](#-enterprise-rag)
3. **Working with relationship-heavy data?** → [Graph RAG](#-graph-rag)
4. **Handling images, videos, audio, charts?** → [Multi-Modal RAG](#-multi-modal-rag)

### Common Prerequisites

All variants require:
- Python 3.9+
- API keys (OpenAI, Anthropic, or similar)
- 2GB+ RAM
- Internet connection (for API calls)

Optional but recommended:
- Docker & Docker Compose
- PostgreSQL (for Enterprise RAG)
- Neo4j (for Graph RAG)
- FFmpeg (for Multi-Modal RAG)

### Environment Setup Template

Each variant includes a `.env.template` file. Standard variables:

```env
# LLM Provider (required)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Vector Database (required)
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west4-gcp-free

# Optional: Specific to variant
# See individual README files for complete list
```

---

## 📈 Architecture Comparison

### Agentic RAG Flow
```
Query → Planner → Retriever → Generator → Critic
  ↓                                          ↓
  └──────────────────┬──────────────────────┘
                     ↓
         More iterations needed?
                ↓        ↓
              Yes      No → Answer
                ↓
         Query Rewriter
```

### Enterprise RAG Flow
```
Query → Multi-Source Retrieval → Re-ranking → LLM Generation → Answer
         ├─ Vector Search
         ├─ BM25 Search
         └─ Metadata Filtering
```

### Graph RAG Flow
```
Query → Entity Search → Path Finding → Context Assembly → LLM Generation
         ↓
         Neo4j Knowledge Graph
```

### Multi-Modal RAG Flow
```
Query → Media Type Detection → Extraction → Embedding → Retrieval → Answer
         ├─ OCR (images)
         ├─ Transcription (video/audio)
         ├─ Parsing (tables/charts)
         └─ Text (documents)
```

---

## 🔧 Configuration Examples

### For Accuracy (Agentic RAG)
```yaml
llm:
  temperature: 0.3
  max_tokens: 2048
loop:
  max_iterations: 5
  confidence_threshold: 0.9
```

### For Scale (Enterprise RAG)
```yaml
retrieval:
  use_bm25: true
  use_reranker: true
  cache:
    enabled: true
    ttl_seconds: 3600
```

### For Relationships (Graph RAG)
```yaml
traversal:
  max_depth: 5
  top_k_paths: 5
  include_all_types: true
```

### For Mixed Media (Multi-Modal RAG)
```yaml
processors:
  enable_ocr: true
  enable_video_transcription: true
  chunk_by_media_type: true
```

---

## 🛠️ Development Workflow

### Clone and Explore

```bash
# Clone repository
git clone <repo-url>
cd RAG

# View available variants
ls -la
# Output:
# Agentic RAG/
# Enterprise RAG/
# Graph RAG/
# Multi Modal RAG/
```

### Set Up Development Environment

```bash
# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Navigate to chosen variant
cd "Agentic RAG"

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API keys
```

### Develop and Test

```bash
# Run tests
pytest tests/ -v

# Run specific variant
python main.py

# Access API documentation
# http://localhost:8000/docs
```

### Deploy

```bash
# Using Docker
docker build -t rag-variant:latest .
docker run -p 8000:8000 --env-file .env rag-variant:latest

# Using Docker Compose
docker-compose up -d

# Using Kubernetes
kubectl apply -f k8s/
```

---

## 📚 Documentation Structure

Each variant has comprehensive documentation:

```
[Variant]/
├── README.md              # Overview and quick start
├── SETUP.md              # Detailed setup guide
├── API.md                # API reference (if applicable)
├── examples/             # Usage examples
├── tests/                # Test suite
└── docs/                 # Additional documentation
```

---

## 🎓 Learning Paths

### Beginner: Start with Multi-Modal RAG
1. Review the architecture diagram
2. Run the quick start example
3. Try indexing your own documents
4. Explore retrieval with media filtering

### Intermediate: Try Agentic RAG
1. Understand the iteration loop
2. Configure LLM parameters
3. Monitor query refinement process
4. Experiment with different queries

### Advanced: Explore Graph RAG
1. Study Neo4j data model
2. Design entity type schemas
3. Analyze graph metrics
4. Implement custom analytics

### Expert: Deploy Enterprise RAG
1. Set up multiple data sources
2. Configure real-time sync
3. Implement security & access control
4. Monitor production system

---

## ⚡ Performance Optimization Tips

### All Variants
- Use batch processing for bulk operations
- Implement caching for repeated queries
- Monitor and optimize embedding dimensions
- Use appropriate LLM models (cost vs. quality)

### Agentic RAG
- Adjust confidence threshold to reduce iterations
- Cache early retrieval results
- Optimize query rewriting strategy

### Enterprise RAG
- Create indexes on frequently searched fields
- Enable BM25 for keyword-heavy queries
- Use incremental sync for large datasets

### Graph RAG
- Create database indexes on entity names
- Limit graph traversal depth
- Use caching for frequent paths

### Multi-Modal RAG
- Use appropriate OCR models
- Batch video processing
- Configure media-type-specific chunking

---

## 🔐 Security Considerations

### API Keys
- Never commit `.env` files
- Use environment variables or secrets management
- Rotate API keys regularly
- Monitor API usage for anomalies

### Data Privacy
- Encrypt data at rest
- Use TLS/HTTPS for all connections
- Implement access controls
- Audit data access logs

### LLM Integration
- Monitor token usage and costs
- Implement rate limiting
- Filter sensitive data before processing
- Comply with data residency requirements

---

## 🐛 Troubleshooting

### Common Issues Across Variants

**API Key Not Found**
```bash
# Verify environment variable is set
echo $OPENAI_API_KEY

# Or in Python
import os
print(os.environ.get('OPENAI_API_KEY'))
```

**Database Connection Failed**
```bash
# Check database is running
# Agentic/Enterprise: Redis/PostgreSQL
# Graph: Neo4j
docker-compose ps
```

**Memory Issues**
```bash
# Reduce batch size in config
# Reduce chunk size
# Process smaller datasets
```

### Variant-Specific Issues

See individual README files:
- [Agentic RAG Troubleshooting](Agentic%20RAG/README.md#troubleshooting)
- [Enterprise RAG Troubleshooting](Enterprise%20RAG/README.md#troubleshooting)
- [Graph RAG Troubleshooting](Graph%20RAG/README.md#troubleshooting)
- [Multi-Modal RAG Troubleshooting](Multi%20Modal%20RAG/README.md#troubleshooting)

---

## 📊 Monitoring & Observability

### Key Metrics by Variant

**Agentic RAG**
- Average iterations per query
- Confidence score distribution
- Iteration improvement rate

**Enterprise RAG**
- Ingestion latency per source
- Query retrieval latency
- Cache hit rate
- Source sync status

**Graph RAG**
- Entity count and types
- Relationship density
- Path traversal time
- Graph query complexity

**Multi-Modal RAG**
- Extraction success rate
- Processing time by media type
- Retrieval quality by type
- Cross-modal match rate

---

## 🤝 Contributing

Contributions welcome! To contribute to any variant:

1. **Fork** the repository
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make changes** and test thoroughly
4. **Commit** with descriptive messages
5. **Push** to your fork
6. **Open Pull Request** with explanation

See individual variant READMEs for specific contribution guidelines.

---

## 📝 License

All variants are licensed under the **MIT License**. See LICENSE file for details.

---

## 🆘 Support & Community

- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Join conversations in GitHub Discussions
- **Documentation**: Check variant-specific README files
- **Examples**: Browse example scripts in each variant

---

## 🎯 Next Steps

1. **Choose a variant** based on your use case
2. **Read the variant's README** for detailed documentation
3. **Follow the quick start** guide
4. **Run examples** to understand the system
5. **Configure for your needs** using the provided templates
6. **Deploy** to production with monitoring

---

## 📌 Quick Links

| Resource | Link |
|----------|------|
| Agentic RAG | [README](Agentic%20RAG/README.md) |
| Enterprise RAG | [README](Enterprise%20RAG/README.md) |
| Graph RAG | [README](Graph%20RAG/README.md) |
| Multi-Modal RAG | [README](Multi%20Modal%20RAG/README.md) |
| API Documentation | See http://localhost:8000/docs (when running) |

---

**Last Updated**: August 2026 | **Version**: 1.0
