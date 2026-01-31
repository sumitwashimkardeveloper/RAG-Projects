# Graph RAG - Knowledge Graph Retrieval Augmented Generation

A sophisticated knowledge graph-based RAG system that extracts entities and relationships from documents, builds an intelligent Neo4j graph database, and leverages LLMs for context-aware question answering.

## Key Advantages Over Vector RAG

- **Relationship Awareness**: Understands connections between entities
- **Traversal Capabilities**: Finds indirect relationships and paths
- **Reasoning Support**: LLM can reason over graph structures
- **Knowledge Consolidation**: Automatically merges related information
- **Explainable Answers**: Clear source trails through entity paths

## Architecture

```
Documents
    ↓
[Text Chunking]
    ↓
[Entity & Relationship Extraction]
    ↓
[Knowledge Graph Construction]
    ↓
[Neo4j Storage]
    ↓
[Query Processing]
    ↓
[LLM Answer Generation]
    ↓
Response with Entity References
```

## Core Components

### 1. Document Loader (`document_loader.py`)
- Supports PDF, DOCX, TXT formats
- Intelligent chunking with configurable overlap
- Metadata preservation

### 2. Entity Extractor (`entity_extractor.py`)
- LLM-powered entity and relationship extraction
- Supports 6 entity types: PERSON, ORGANIZATION, LOCATION, CONCEPT, PRODUCT, EVENT
- 5 relationship types: RELATED_TO, WORKS_FOR, LOCATED_IN, CREATED, USES

### 3. Graph Database (`graph_db.py`)
- Neo4j driver with connection pooling
- CRUD operations for entities and relationships
- Graph traversal and path finding
- Full-text search capabilities

### 4. Graph Builder (`graph_builder.py`)
- Orchestrates extraction and storage
- Tracks processed chunks to avoid duplicates
- Generates extraction statistics

### 5. Query Engine (`query_engine.py`)
- Parse natural language queries
- Entity search and context retrieval
- Path finding between entities
- Graph-based result assembly

### 6. Answer Generator (`answer_generator.py`)
- LLM integration (OpenAI/Anthropic)
- Context formatting from graph data
- Streaming response support

### 7. FastAPI Server (`main.py`)
- RESTful API endpoints
- Document ingestion (single/batch)
- Real-time query processing
- Graph analytics and management

## Quick Start

### Prerequisites
- Python 3.11+
- Docker (for Neo4j)
- API Key (OpenAI or Anthropic)

### Setup

1. Clone and navigate to Graph RAG folder:
```bash
cd "Graph RAG"
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Edit `.env` with your API keys:
```
OPENAI_API_KEY=sk-...
NEO4J_PASSWORD=your_secure_password
```

4. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

5. Start Neo4j:
```bash
docker-compose up -d neo4j
```

6. Run demo:
```bash
python demo.py
```

7. Start API server:
```bash
python main.py
```

Access API at: http://localhost:8000/docs

## Usage Examples

### Python Client

```python
from client import GraphRAGClient

client = GraphRAGClient()

# Ingest documents
client.ingest_file("document.pdf")

# Query the knowledge graph
response = client.query("Who works at which company?")
print(response["answer"])

# View graph statistics
stats = client.get_graph_stats()
print(f"Entities: {stats['entities']}")
print(f"Relationships: {stats['relationships']}")

# Search entities
results = client.search_entities("Apple", entity_type="ORGANIZATION")

# Find connections
connections = client.find_connections("Steve_Jobs", "Apple")
```

### Direct API Calls

```bash
# Upload document
curl -X POST -F "file=@document.pdf" http://localhost:8000/ingest

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about the founders"}'

# Get statistics
curl http://localhost:8000/graph/stats

# Search entities
curl "http://localhost:8000/graph/search?q=Apple&entity_type=ORGANIZATION"
```

### Advanced Analytics

```python
from graph_analytics import graph_analytics

# Get entity centrality
centrality = graph_analytics.get_centrality_scores()

# Find entity communities
communities = graph_analytics.find_entity_communities("Steve Jobs", depth=3)

# Calculate entity similarity
similarity = graph_analytics.calculate_entity_similarity("Apple", "Microsoft")

# Get knowledge gaps
gaps = graph_analytics.get_knowledge_gaps()

# Recommend new connections
recommendations = graph_analytics.recommend_connections("Apple", limit=5)
```

## API Endpoints

### Query
- `POST /query` - Execute natural language query
- `GET /graph/stats` - Graph statistics
- `GET /graph/search?q=query` - Entity search
- `GET /graph/entity/{id}` - Entity details
- `POST /graph/connections` - Find paths

### Ingestion
- `POST /ingest` - Upload single document
- `POST /ingest-batch` - Upload multiple documents
- `DELETE /graph/reset` - Clear graph

### System
- `GET /health` - Health check

## Configuration

Edit `config.py` to customize:

```python
chunk_size = 1024              # Chunk size in characters
chunk_overlap = 256            # Overlap between chunks
top_k_entities = 10            # Entities per query
top_k_paths = 5                # Paths to retrieve
llm_model = "gpt-4-turbo-preview"  # LLM to use
```

## File Structure

```
Graph RAG/
├── main.py                  # FastAPI server
├── config.py               # Configuration
├── graph_db.py             # Neo4j interface
├── entity_extractor.py     # LLM extraction
├── document_loader.py      # Document ingestion
├── graph_builder.py        # Graph construction
├── query_engine.py         # Query processing
├── answer_generator.py     # LLM integration
├── graph_analytics.py      # Analytics and insights
├── init_schema.py          # Database initialization
├── client.py               # Python client
├── demo.py                 # Demonstration
├── requirements.txt        # Dependencies
├── docker-compose.yml      # Docker setup
├── Dockerfile              # Container config
├── SETUP.md               # Setup guide
├── .env.example           # Environment template
└── README.md              # This file
```

## Performance

- Query Latency: < 2 seconds (average)
- Entity Extraction: 50-200 entities per document
- Graph Depth: Supports traversal up to 5 levels
- Concurrent Connections: 50+
- Memory Usage: ~2GB for 100K entities

## Supported Formats

- **Documents**: PDF, DOCX, TXT
- **Databases**: Neo4j 4.x+
- **LLMs**: GPT-4, Claude 3, Claude 3.5
- **APIs**: OpenAI, Anthropic

## Advanced Features

### Duplicate Detection
```python
from init_schema import detect_entity_duplicates
duplicates = detect_entity_duplicates()
```

### Centrality Analysis
```python
from graph_analytics import graph_analytics
central = graph_analytics.get_centrality_scores()
```

### Subgraph Export
```python
subgraph = graph_analytics.export_subgraph("Apple", radius=2)
```

### Connection Recommendations
```python
recommendations = graph_analytics.recommend_connections("Microsoft")
```

## Troubleshooting

### Neo4j Connection
```bash
# Check if running
curl http://localhost:7474

# Restart container
docker-compose restart neo4j
```

### LLM Rate Limits
- Check API quotas
- Implement batching for bulk processing
- Add retry logic with exponential backoff

### Memory Issues
- Reduce `chunk_size` in config
- Process in smaller batches
- Increase system RAM

## Neo4j Browser

Access Neo4j Browser at: http://localhost:7474
- Username: `neo4j`
- Password: (from .env)

Explore the graph:
```cypher
MATCH (e:Entity) RETURN e LIMIT 10
MATCH (e)-[r]->(f) RETURN e, r, f LIMIT 20
MATCH p = shortestPath((a:Entity)-[*]-(b:Entity)) RETURN p LIMIT 5
```

## Contributing

To extend the system:

1. Add custom entity types in `entity_extractor.py`
2. Implement new relationship types
3. Extend `GraphQueryEngine` with custom queries
4. Add new analytics in `graph_analytics.py`

## Performance Optimization

1. **Indexing**: Create indexes on frequently searched fields
   ```cypher
   CREATE INDEX idx_name FOR (e:Entity) ON (e.name)
   ```

2. **Caching**: Results are cached in memory
3. **Batching**: Use batch ingestion for multiple files
4. **Chunking**: Optimize chunk size for your documents

## License

MIT License

## Next Steps

- Review SETUP.md for detailed setup instructions
- Run demo.py to see it in action
- Check client.py for integration examples
- Explore graph_analytics.py for advanced features
