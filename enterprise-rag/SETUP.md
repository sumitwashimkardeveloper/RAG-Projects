# Step 1: Environment Setup & Dependencies - Complete Guide

This guide walks through the complete setup process for the Enterprise Knowledge RAG backend development environment.

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.10 or higher
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **Git**: 2.0 or higher

### Required Tools
- Python virtual environment (venv or conda)
- pip or poetry
- PostgreSQL client tools (psql)
- Redis CLI

## Installation Steps

### 1. Clone and Setup Local Repository

```bash
# Clone the repository
git clone <repository-url>
cd enterprise-rag

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Python Dependencies

#### Option A: Using pip (requirements.txt)
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### Option B: Using pip with pyproject.toml (Modern approach)
```bash
pip install --upgrade pip setuptools wheel
pip install -e .

# For development dependencies:
pip install -e ".[dev]"

# For ML/local embedding models:
pip install -e ".[ml]"
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Key variables to set:**
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_HOST`: Redis server address
- `PINECONE_API_KEY`: Pinecone vector database key
- Source credentials (Confluence, Notion, SharePoint, etc.)

### 4. Start Infrastructure Services

#### Using Docker Compose (Recommended)
```bash
# Start all services (PostgreSQL, Redis, Weaviate, Prometheus, Grafana)
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Stop services
docker-compose down
```

#### Manual Installation (Optional)

**PostgreSQL:**
```bash
# macOS with Homebrew
brew install postgresql
brew services start postgresql

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start

# Windows
# Download from https://www.postgresql.org/download/windows/
```

**Redis:**
```bash
# macOS with Homebrew
brew install redis
brew services start redis

# Linux (Ubuntu/Debian)
sudo apt-get install redis-server
sudo service redis-server start

# Windows
# Use Windows Subsystem for Linux (WSL) or download binary
```

### 5. Initialize Database

```bash
# Create database and user (if using manual setup)
psql -U postgres -c "CREATE USER rag_user WITH PASSWORD 'rag_password';"
psql -U postgres -c "CREATE DATABASE enterprise_rag OWNER rag_user;"

# Run migrations (when implemented)
alembic upgrade head

# Or let the app auto-create tables on startup
python main.py
```

### 6. Verify Installation

```bash
# Check Python packages
pip list

# Test database connection
python -c "from app.database import init_db; print('Database module imported successfully')"

# Test Redis connection
redis-cli ping

# Start the API server (development)
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Verify Services are Running

Open in browser:
- **API Documentation**: http://localhost:8000/api/docs
- **API Health Check**: http://localhost:8000/health
- **Prometheus Metrics**: http://localhost:9090
- **Grafana Dashboard**: http://localhost:3000 (login: admin/admin)
- **Weaviate Console**: http://localhost:8080/v1/objects

## Project Structure

```
enterprise-rag/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection
│   ├── logging_config.py      # Logging setup
│   ├── connectors/            # Data source connectors (Step 2)
│   ├── ingestion/             # Ingestion pipeline (Step 2)
│   ├── processing/            # Text processing (Step 3)
│   ├── embeddings/            # Embedding service (Step 4)
│   ├── retrieval/             # Retrieval system (Step 5)
│   ├── llm/                   # LLM integration (Step 6)
│   ├── api/                   # API endpoints (Step 7)
│   ├── models/                # Database models
│   └── utils/                 # Utility functions
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
├── migrations/                # Alembic migrations
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Modern project configuration
├── Dockerfile                 # Container image
├── docker-compose.yml         # Multi-container orchestration
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
python main.py --port 8001
```

### PostgreSQL Connection Issues
```bash
# Test connection
psql -h localhost -U rag_user -d enterprise_rag

# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql.log
```

### Redis Connection Issues
```bash
# Test Redis connection
redis-cli -h localhost -p 6379 ping

# Check Redis logs
redis-cli info
```

### Module Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/enterprise-rag"

# Verify installation
python -c "import app; print(app.__version__)"
```

### Database Errors
```bash
# Reset database (WARNING: Deletes all data)
python -c "from app.database import Base, engine; Base.metadata.drop_all(engine)"

# Restart services
docker-compose restart postgres redis
```

## Environment Checklist

Before proceeding to Step 2, verify:

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies from requirements.txt installed
- [ ] Docker and Docker Compose running
- [ ] PostgreSQL database accessible
- [ ] Redis server accessible
- [ ] API server starts without errors
- [ ] Health check endpoint responds (GET /health)
- [ ] API documentation loads (http://localhost:8000/api/docs)

## Next Steps

After completing Step 1:
1. Proceed to **Step 2: Data Ingestion Pipeline** to implement data source connectors
2. Review configuration in `.env` for your specific data sources
3. Set up API credentials for Confluence, Notion, SharePoint, Google Drive, etc.
4. Prepare test documents for ingestion testing

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Async Guide](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

## Support

For issues:
1. Check logs: `docker-compose logs -f postgres`
2. Review .env configuration
3. Verify all services are running: `docker-compose ps`
4. Check port availability: `netstat -tlnp`
5. Review error messages in terminal output

---

**Status**: Step 1 Complete ✅
**Next**: Step 2 - Data Ingestion Pipeline
