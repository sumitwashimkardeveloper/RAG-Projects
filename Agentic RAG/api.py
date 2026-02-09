from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn
from pathlib import Path

from modules.utils import get_logger, get_config
from pipeline import AgenticRAGPipeline

logger = get_logger(__name__, log_file=str(Path("logs") / "api.log"))

app = FastAPI(
    title="Agentic RAG API",
    description="Retrieval Augmented Generation with Agentic Loop",
    version="1.0.0"
)

config = get_config()
pipeline = AgenticRAGPipeline(config)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    max_iterations: int = 5
    include_metadata: bool = True

class Document(BaseModel):
    id: str
    content: str
    source: str
    score: float

class Citation(BaseModel):
    source: str
    snippet: str
    relevance_score: float

class QueryResponse(BaseModel):
    query: str
    answer: str
    documents: List[Document]
    citations: List[Citation]
    confidence: float
    iterations: int
    success: bool

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        components={
            "planner": "ready",
            "retriever": "ready",
            "critic": "ready",
            "query_rewriter": "ready",
            "answer_generator": "ready"
        }
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, background_tasks: BackgroundTasks):
    try:
        logger.info(f"Processing query: {request.query}")

        result = pipeline.process(request.query)

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))

        documents = []
        for doc in result.get("documents", []):
            if isinstance(doc, dict):
                documents.append(Document(
                    id=doc.get("id", "unknown"),
                    content=doc.get("metadata", {}).get("content", "")[:200],
                    source=doc.get("metadata", {}).get("source", ""),
                    score=doc.get("score", 0)
                ))

        citations = []
        answer_metadata = result.get("metadata", {}).get("answer", {})
        for citation_data in answer_metadata.get("citations", [])[:5]:
            citations.append(Citation(
                source=citation_data.get("source", ""),
                snippet=citation_data.get("snippet", "")[:100],
                relevance_score=0.8
            ))

        iterations_data = result.get("iterations", {})

        response = QueryResponse(
            query=request.query,
            answer=result.get("answer", ""),
            documents=documents,
            citations=citations,
            confidence=float(iterations_data.get("avg_confidence", 0.0)),
            iterations=iterations_data.get("total_iterations", 0),
            success=True
        )

        background_tasks.add_task(log_query_metrics, request.query, result)

        logger.info(f"Query processed successfully in {iterations_data.get('total_iterations', 0)} iterations")
        return response

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def get_metrics():
    stats = pipeline.get_pipeline_statistics()
    return {
        "pipeline_stats": stats,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/evaluate")
async def evaluate_answer(query: str, answer: str, documents: List[Dict[str, Any]]):
    try:
        is_valid, score, issues = pipeline.answer_generator.validate_answer(answer, query, documents)

        return {
            "is_valid": is_valid,
            "score": score,
            "issues": issues,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error evaluating answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info")
async def get_info():
    return {
        "name": "Agentic RAG",
        "version": "1.0.0",
        "components": [
            "Query Planner",
            "Retriever",
            "Critic",
            "Query Rewriter",
            "Answer Generator"
        ],
        "max_iterations": config.get("loop.max_iterations", 5),
        "timeout_seconds": config.get("loop.iteration_timeout", 60)
    }

def log_query_metrics(query: str, result: Dict[str, Any]):
    logger.info(f"Query metrics - Query: {query[:50]}... | Iterations: {result.get('iterations', {}).get('total_iterations', 0)} | Success: {result.get('success')}")

if __name__ == "__main__":
    host = config.get("api.host", "0.0.0.0")
    port = config.get("api.port", 8000)
    debug = config.get("api.debug", False)

    uvicorn.run(app, host=host, port=port, debug=debug)
