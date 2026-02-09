# Agentic RAG Deployment Guide

## Quick Start

### 1. Local Development

```bash
python -m pip install -r requirements.txt
python -m pytest tests/
python api.py
```

### 2. Docker Deployment

```bash
docker-compose up -d
```

## Full Deployment Process

### Step 1: Environment Setup

```bash
python deploy.py --setup
```

This creates necessary directories and configures the environment.

### Step 2: Install Dependencies

```bash
python deploy.py --install
```

### Step 3: Run Tests

```bash
python deploy.py --test
```

### Step 4: Build Docker Image

```bash
python deploy.py --docker-build
```

### Step 5: Start Services

```bash
python deploy.py --docker-start
```

### Step 6: Verify Deployment

```bash
python deploy.py --verify
```

### Complete Automated Deployment

```bash
python deploy.py --full
```

## API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Query Processing

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?"}'
```

### Metrics

```bash
curl http://localhost:8000/metrics
```

## Performance Testing

```bash
python performance_test.py
```

## Configuration

Edit `configs/config.yaml` to customize:
- LLM settings
- Vector database configuration
- Retriever parameters
- Iteration limits
- API settings

## Monitoring

Metrics are stored in `logs/metrics.json` and accessible via `/metrics` endpoint.

## Troubleshooting

1. Check logs: `tail -f logs/agentic_rag.log`
2. Verify dependencies: `pip list | grep -E 'langchain|pinecone|fastapi'`
3. Test connectivity: `curl http://localhost:8000/health`
