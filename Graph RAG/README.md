# Graph RAG - Knowledge Graph Retrieval Augmented Generation

A sophisticated **knowledge graph-based RAG system** that extracts entities and relationships from documents, constructs a Neo4j knowledge graph, and leverages LLMs for intelligent, explainable question answering through graph reasoning.

## Key Features

🔗 **Relationship Awareness** - Understands connections between entities, not just keywords  
🧭 **Path Finding** - Discovers indirect relationships and connection paths  
🎯 **Entity-Centric Reasoning** - LLM reasoning over graph structures  
📊 **Knowledge Consolidation** - Automatically merges related information  
🔍 **Explainable Answers** - Clear source trails through entity relationships  
⚡ **Real-time Analysis** - Fast graph traversal and querying  
📈 **Graph Analytics** - Entity centrality, community detection, recommendations  

## Why Graph RAG?

| Aspect | Vector RAG | Graph RAG |
|--------|-----------|----------|
| **Understanding** | Keyword similarity | Semantic relationships |
| **Queries** | "Find similar content" | "Show all companies founded by X" |
| **Reasoning** | Direct context matching | Multi-hop graph traversal |
| **Explainability** | Top-k similar chunks | Entity paths and connections |
| **Knowledge Updates** | Re-embed everything | Add/update nodes & edges |
| **Complex Relations** | Limited | Native support |

## Architecture

```
Documents
    ↓
[Text Chunking]
    - Intelligent document splitting
    - Metadata preservation
    ↓
[Entity & Relationship Extraction]
    - LLM-powered extraction
    - Entity deduplication
    - Relationship classification
    ↓
[Knowledge Graph Construction]
    - Entity nodes creation
    - Relationship edge creation
    - Graph optimization
    ↓
[Neo4j Storage]
    - Property graph storage
    - Index creation
    - Concurrent access support
    ↓
[Query Processing]
    - Natural language parsing
    - Entity search
    - Path finding
    ↓
[LLM Answer Generation]
    - Context formatting from graph
    - Answer synthesis
    - Citation generation
    ↓
Response with Entity References
```

## Installation

### Prerequisites

```
Python 3.11+
Docker (for Neo4j)
API Key (OpenAI or Anthropic)
```

### Quick Setup

1. **Navigate to folder:**
```bash
cd "Graph RAG"
```

2. **Create environment file:**
```bash
cp .env.example .env
```

3. **Configure API keys:**
```env
# LLM Provider
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
LLM_PROVIDER=openai

# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_secure_password
NEO4J_DATABASE=neo4j

# Logging
LOG_LEVEL=INFO
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

5. **Start Neo4j:**
```bash
docker-compose up -d neo4j
```

6. **Initialize graph schema:**
```bash
python init_schema.py
```

## Quick Start

### 1. Ingest Documents

```python
from graph_builder import GraphRAGBuilder

builder = GraphRAGBuilder()

# Ingest single document
builder.ingest_file("document.pdf")

# Or batch ingest
builder.ingest_directory("./documents/")

# Check statistics
stats = builder.get_stats()
print(f"Entities: {stats['entity_count']}")
print(f"Relationships: {stats['relationship_count']}")
```

### 2. Query the Graph

```python
from query_engine import QueryEngine

engine = QueryEngine()

# Search entities
results = engine.search_entities("Steve Jobs", entity_type="PERSON")
for entity in results:
    print(f"- {entity['name']} ({entity['type']})")

# Find connections
connections = engine.find_connections("Steve Jobs", "Apple")
print(f"Shortest path: {connections['shortest_path']}")
```

### 3. Generate Answer

```python
from answer_generator import AnswerGenerator

generator = AnswerGenerator()

answer = generator.generate(
    query="Who founded Apple?",
    context=graph_context
)

print(f"Answer: {answer['text']}")
print(f"Sources: {answer['citations']}")
```

### 4. Analyze Graph

```python
from graph_analytics import GraphAnalytics

analytics = GraphAnalytics()

# Entity centrality (most important entities)
centrality = analytics.get_centrality_scores()
for entity, score in centrality[:10]:
    print(f"{entity}: {score:.3f}")

# Find entity communities
communities = analytics.find_communities(max_depth=3)

# Get entity recommendations
recommendations = analytics.recommend_connections("Microsoft", limit=5)
```

## API Endpoints

### Query Endpoints

```
POST   /query                  - Execute natural language query
GET    /graph/stats            - Graph statistics
GET    /graph/search?q=...     - Search entities
GET    /graph/entity/{id}      - Get entity details
POST   /graph/connections      - Find paths between entities
```

### Ingestion Endpoints

```
POST   /ingest                 - Upload single document
POST   /ingest-batch           - Upload multiple documents
DELETE /graph/reset            - Clear entire graph
GET    /graph/status           - Graph status
```

### Analytics Endpoints

```
GET    /analytics/centrality   - Entity centrality scores
GET    /analytics/communities  - Entity communities
GET    /analytics/duplicates   - Potential duplicate entities
```

### System Endpoints

```
GET    /health                 - Health check
GET    /version                - API version
POST   /health/detailed        - Detailed health info
```

## Core Components

### 1. Document Loader (`document_loader.py`)

Handles PDF, DOCX, TXT formats with intelligent chunking:

```python
from document_loader import DocumentLoader

loader = DocumentLoader(
    chunk_size=1024,
    chunk_overlap=256
)

chunks = loader.load_pdf("document.pdf")
chunks = loader.load_docx("document.docx")
chunks = loader.load_text("document.txt")
```

### 2. Entity Extractor (`entity_extractor.py`)

LLM-powered entity and relationship extraction:

**Supported Entity Types:**
- `PERSON` - Individual people
- `ORGANIZATION` - Companies, institutions
- `LOCATION` - Geographic locations
- `CONCEPT` - Abstract ideas, technologies
- `PRODUCT` - Products, services
- `EVENT` - Events, meetings

**Supported Relationship Types:**
- `RELATED_TO` - Generic relationship
- `WORKS_FOR` - Person works at organization
- `LOCATED_IN` - Entity located at place
- `CREATED` - Created a product/concept
- `USES` - Organization uses product

```python
from entity_extractor import EntityExtractor

extractor = EntityExtractor()

# Extract entities and relationships
entities, relationships = extractor.extract(text)

for entity in entities:
    print(f"{entity['id']}: {entity['name']} ({entity['type']})")

for rel in relationships:
    print(f"{rel['source']} --{rel['type']}--> {rel['target']}")
```

### 3. Graph Database (`graph_db.py`)

Neo4j interface with connection pooling and full-text search:

```python
from graph_db import GraphDatabase

db = GraphDatabase()

# CRUD operations
db.create_entity(name="Apple", entity_type="ORGANIZATION")
db.create_relationship("Steve_Jobs", "WORKS_FOR", "Apple")

# Traversal
paths = db.find_shortest_path("Steve Jobs", "Microsoft", max_depth=5)

# Full-text search
results = db.full_text_search("iPhone", limit=10)
```

### 4. Graph Builder (`graph_builder.py`)

Orchestrates extraction and storage:

```python
from graph_builder import GraphRAGBuilder

builder = GraphRAGBuilder()

# Process document
result = builder.process_document("document.pdf")
print(f"Extracted {result['entity_count']} entities")
print(f"Extracted {result['relationship_count']} relationships")
```

### 5. Query Engine (`query_engine.py`)

Parse natural language and retrieve from graph:

```python
from query_engine import QueryEngine

engine = QueryEngine()

# Entity search
results = engine.search_entities("Apple", entity_type="ORGANIZATION")

# Find connections
paths = engine.find_connections("Jobs", "Microsoft", depth=3)

# Get entity context
context = engine.get_entity_context("Apple", depth=2)
```

### 6. Answer Generator (`answer_generator.py`)

LLM-based answer generation with streaming:

```python
from answer_generator import AnswerGenerator

generator = AnswerGenerator()

# Generate with streaming
for chunk in generator.generate_stream(query, context):
    print(chunk, end='', flush=True)
```

### 7. Graph Analytics (`graph_analytics.py`)

Advanced graph analysis and insights:

```python
from graph_analytics import GraphAnalytics

analytics = GraphAnalytics()

# Centrality analysis
scores = analytics.get_centrality_scores()

# Community detection
communities = analytics.find_entity_communities("Apple", depth=3)

# Duplicate detection
duplicates = analytics.detect_entity_duplicates(similarity_threshold=0.8)

# Connection recommendations
recommendations = analytics.recommend_connections("Microsoft", limit=5)
```

## Configuration

### Edit `config.py`

```python
# Document Processing
chunk_size = 1024                      # Characters per chunk
chunk_overlap = 256                    # Overlap between chunks

# Entity Extraction
entity_types = ['PERSON', 'ORGANIZATION', 'LOCATION', 'CONCEPT', 'PRODUCT', 'EVENT']
relationship_types = ['RELATED_TO', 'WORKS_FOR', 'LOCATED_IN', 'CREATED', 'USES']

# Graph Settings
top_k_entities = 10                    # Entities to retrieve per query
top_k_paths = 5                        # Paths to return
max_traversal_depth = 5                # Maximum graph depth

# LLM Configuration
llm_model = "gpt-4-turbo-preview"     # Or "claude-3-opus-20240229"
llm_temperature = 0.3                  # Lower = more deterministic
llm_max_tokens = 2048

# Neo4j Connection
neo4j_uri = "bolt://localhost:7687"
neo4j_auth = ("neo4j", "password")
neo4j_database = "neo4j"

# Performance
batch_size = 32                        # Batch processing size
connection_pool_size = 50              # Neo4j connection pool
```

## File Structure

```
Graph RAG/
├── main.py                     # FastAPI server entry point
├── config.py                   # Configuration settings
├── init_schema.py             # Database schema initialization
├── client.py                   # Python client library
├── demo.py                     # Interactive demo
├── requirements.txt            # Python dependencies
├── docker-compose.yml         # Docker setup
├── Dockerfile                 # Container config
├── .env.example               # Environment template
│
├── Core Modules/
│   ├── document_loader.py     # PDF, DOCX, TXT parsing
│   ├── entity_extractor.py    # LLM-powered extraction
│   ├── graph_db.py            # Neo4j interface
│   ├── graph_builder.py       # Orchestration
│   ├── query_engine.py        # Natural language queries
│   ├── answer_generator.py    # LLM answer generation
│   └── graph_analytics.py     # Graph analysis & insights
│
├── API/
│   └── [FastAPI endpoints defined in main.py]
│
├── Tests/
│   ├── test_entity_extractor.py
│   ├── test_graph_db.py
│   ├── test_query_engine.py
│   └── test_answer_generator.py
│
├── Docs/
│   ├── SETUP.md              # Detailed setup guide
│   └── API.md                # API documentation
│
└── README.md                  # This file
```

## Usage Examples

### Example 1: Basic Query

```python
from client import GraphRAGClient

client = GraphRAGClient()

# Ingest documents
client.ingest_file("document.pdf")

# Query
response = client.query("Who works at which company?")
print(response["answer"])
print(f"Confidence: {response['confidence']}")
```

### Example 2: Entity Search

```python
# Search by entity type
organizations = client.search_entities("Apple", entity_type="ORGANIZATION")
people = client.search_entities("Steve", entity_type="PERSON")

# Get entity details
entity = client.get_entity("Apple_Inc")
print(f"Name: {entity['name']}")
print(f"Type: {entity['type']}")
print(f"Properties: {entity['properties']}")
```

### Example 3: Path Finding

```python
# Find shortest path
paths = client.find_connections("Steve_Jobs", "Apple", max_depth=3)
for path in paths[:3]:
    print(f"Path: {' -> '.join(path)}")

# Analyze relationship strength
strength = client.analyze_connection("Jobs", "Apple")
print(f"Connection strength: {strength}")
```

### Example 4: Analytics

```python
# Get most important entities
analytics = client.get_graph_analytics()
print(f"Top entities by centrality:")
for entity, score in analytics['top_entities'][:10]:
    print(f"  {entity}: {score:.3f}")

# Find related entities
similar = client.find_similar_entities("Microsoft")
print(f"Entities similar to Microsoft: {similar}")
```

### Example 5: Direct API Calls

```bash
# Search entities
curl "http://localhost:8000/graph/search?q=Apple&entity_type=ORGANIZATION"

# Upload document
curl -X POST -F "file=@document.pdf" http://localhost:8000/ingest

# Query graph
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about the founders"}'

# Get statistics
curl http://localhost:8000/graph/stats
```

## Performance Characteristics

| Metric | Target | Typical |
|--------|--------|---------|
| Query Latency | < 2s | 0.8-1.5s |
| Entity Extraction | 50-200 entities/doc | 120/doc |
| Graph Traversal | 5+ levels | O(n) time |
| Concurrent Connections | 50+ | Tested to 100+ |
| Memory Usage | 2GB for 100K entities | Scales linearly |

## Database Supported Formats

| Component | Support |
|-----------|---------|
| Documents | PDF, DOCX, TXT |
| Databases | Neo4j 4.x+ |
| LLMs | GPT-4, Claude 3, Claude 3.5 |
| APIs | OpenAI, Anthropic |

## Advanced Features

### Duplicate Detection

```python
from init_schema import detect_entity_duplicates

duplicates = detect_entity_duplicates(similarity_threshold=0.8)
for group in duplicates:
    print(f"Potential duplicates: {group}")
    # Merge or review manually
```

### Centrality Analysis

```python
from graph_analytics import graph_analytics

# Betweenness centrality
centrality = graph_analytics.get_centrality_scores()

# Degree analysis
degrees = graph_analytics.get_entity_degrees()
```

### Subgraph Export

```python
subgraph = graph_analytics.export_subgraph("Apple", radius=2)
# Export as Cypher, JSON, or visualization
subgraph.export_cypher("apple_subgraph.cypher")
```

### Connection Recommendations

```python
recommendations = graph_analytics.recommend_connections("Microsoft", limit=5)
for rec in recommendations:
    print(f"Consider connecting to: {rec['entity']} (score: {rec['score']})")
```

## Troubleshooting

### Neo4j Connection Issues

```bash
# Check if Neo4j is running
curl http://localhost:7474

# View logs
docker-compose logs neo4j

# Restart
docker-compose restart neo4j
```

### LLM Rate Limits

- Check API quotas in provider console
- Implement batching for bulk processing
- Add retry logic with exponential backoff
- Monitor token usage

### Memory Issues

```python
# Reduce chunk size
config.chunk_size = 512

# Process in smaller batches
builder.ingest_directory("./docs", batch_size=10)

# Increase system RAM or add swap
```

### Slow Queries

```cypher
# Create indexes for common searches
CREATE INDEX idx_entity_name FOR (e:Entity) ON (e.name)
CREATE INDEX idx_entity_type FOR (e:Entity) ON (e.type)

# Check query plans
EXPLAIN MATCH (a:Entity)-[r]->(b:Entity) RETURN a, r, b
```

## Neo4j Browser

Access Neo4j Browser: **http://localhost:7474**

**Credentials:**
- Username: `neo4j`
- Password: (from .env)

### Useful Cypher Queries

```cypher
# View all entities
MATCH (e:Entity) RETURN e LIMIT 100

# Show all relationships
MATCH (e)-[r]->(f) RETURN e, r, f LIMIT 50

# Find shortest path
MATCH p = shortestPath((a:Entity)-[*]-(b:Entity))
WHERE a.name = 'Steve Jobs' AND b.name = 'Apple'
RETURN p

# Degree distribution
MATCH (e:Entity)-[r]->()
RETURN e.type, COUNT(r) as degree
ORDER BY degree DESC

# Delete specific entities
MATCH (e:Entity {name: 'Duplicate Name'})
DETACH DELETE e
```

## Performance Optimization

### Indexing Strategy

```cypher
-- Create indexes on frequently searched fields
CREATE INDEX idx_name FOR (e:Entity) ON (e.name)
CREATE INDEX idx_type FOR (e:Entity) ON (e.type)
CREATE INDEX idx_rel_type FOR ()-[r:RELATIONSHIP]-() ON (r.type)
```

### Query Optimization

```python
# Use filters early
results = engine.search_entities(
    "Apple",
    entity_type="ORGANIZATION",  # Filter early
    limit=10                      # Limit results
)

# Cache frequently accessed entities
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_entity_context(entity_id):
    return db.get_entity_context(entity_id)
```

### Caching

```python
# Results are cached in memory by default
# Configure cache settings
cache.max_size = 10000
cache.ttl_seconds = 3600
```

## Development & Contributing

### Run Tests

```bash
pytest tests/ -v

# With coverage
pytest --cov=. tests/

# Specific test
pytest tests/test_query_engine.py -v
```

### Extend the System

1. Add custom entity types in `entity_extractor.py`
2. Implement new relationship types
3. Extend `QueryEngine` with custom queries
4. Add analytics methods in `graph_analytics.py`
5. Submit PR with tests

## Deployment

### Docker Compose

```bash
docker-compose up -d
curl http://localhost:8000/health
```

### Kubernetes

```bash
kubectl apply -f k8s/
kubectl get pods -l app=graph-rag
```

## License

MIT License - See LICENSE file for details

## Next Steps

1. Review [SETUP.md](SETUP.md) for detailed setup instructions
2. Run `demo.py` to see it in action
3. Check [API.md](docs/API.md) for complete API reference
4. Explore `graph_analytics.py` for advanced features
5. Join discussions for questions and feature requests
