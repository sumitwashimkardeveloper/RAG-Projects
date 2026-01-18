# Quick Start Guide - Enterprise Knowledge RAG

Get the backend up and running in 5 minutes.

## Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Git

## Step 1: Clone & Setup (2 min)

```bash
# Clone repository
git clone <repository-url>
cd enterprise-rag

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment (1 min)

```bash
# Create .env file from template
cp .env.example .env

# Edit .env with required API keys (optional for basic testing)
# Required keys: OPENAI_API_KEY, DATABASE_URL (auto-configured with Docker)
```

## Step 3: Start Services (1 min)

```bash
# Start PostgreSQL, Redis, Weaviate, and monitoring stack
docker-compose up -d

# Wait for services to be healthy (about 30 seconds)
docker-compose ps
```

## Step 4: Run Server (1 min)

```bash
# Start development server
python main.py

# Server will start at http://localhost:8000
```

## Step 5: Verify Setup (1 min)

Open in browser:
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health
- **Grafana**: http://localhost:3000 (admin/admin)

That's it! ✅

---

## Common Commands

### Development
```bash
# Run with auto-reload
make run-dev

# Run tests
make test

# Format & lint code
make format
make lint
```

### Database
```bash
# Initialize database
make db-init

# Reset database (⚠️ deletes all data)
make db-reset
```

### Docker
```bash
# View logs
make docker-logs

# Stop services
make docker-down

# Restart services
docker-compose restart
```

### Advanced
```bash
# Start Celery worker (background tasks)
make worker

# Access PostgreSQL
docker-compose exec postgres psql -U rag_user -d enterprise_rag

# Access Redis
redis-cli

# View API metrics
http://localhost:9090  # Prometheus
```

## Project Structure

```
enterprise-rag/
├── app/                    # Application code
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── .env.example            # Configuration template
├── docker-compose.yml      # Services (PostgreSQL, Redis, etc.)
├── Dockerfile              # Container image
└── Makefile                # Common commands
```

## Troubleshooting

### Server won't start
```bash
# Kill process on port 8000
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Try again
python main.py
```

### Database connection error
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Restart if needed
docker-compose restart postgres
```

### Port already in use
```bash
# Use different port
uvicorn main:app --port 8001
```

### Virtual environment issues
```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

1. **Add API Keys**: Edit `.env` with your OpenAI, Confluence, Notion credentials
2. **Read SETUP.md**: Full installation & configuration guide
3. **Start Step 2**: Data ingestion pipeline implementation
4. **Check API Docs**: Visit http://localhost:8000/api/docs for available endpoints

## Environment Details

- **Framework**: FastAPI (modern Python web framework)
- **Database**: PostgreSQL (with SQLAlchemy ORM)
- **Cache**: Redis (caching & session management)
- **Vector DB**: Weaviate (semantic search)
- **LLM**: OpenAI GPT-4 (configurable)
- **Monitoring**: Prometheus + Grafana

## Getting Help

- Check logs: `docker-compose logs -f`
- Review SETUP.md for detailed configuration
- Check API documentation: http://localhost:8000/api/docs
- See Makefile for all available commands

---

**Status**: Ready to develop! 🚀
