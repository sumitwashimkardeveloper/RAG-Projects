from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import os
import tempfile
from config import settings
from document_loader import document_loader
from graph_builder import graph_builder
from query_engine import query_engine
from answer_generator import answer_generator
from graph_db import graph_db

app = FastAPI(
    title="Graph RAG API",
    description="Knowledge Graph-based Retrieval Augmented Generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str
    context_used: str

class GraphStatsResponse(BaseModel):
    entities: int
    relationships: int

class HealthResponse(BaseModel):
    status: str
    graph_stats: dict

@app.on_event("startup")
async def startup_event():
    print("Graph RAG API started")

@app.on_event("shutdown")
async def shutdown_event():
    graph_db.close()
    print("Graph RAG API shutdown")

@app.get("/health", response_model=HealthResponse)
async def health():
    stats = graph_db.get_graph_stats()
    return {
        "status": "healthy",
        "graph_stats": stats
    }

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        graph_context = query_engine.execute_graph_query(request.query)

        result = answer_generator.generate_answer(request.query, graph_context)

        return QueryResponse(
            query=result["query"],
            answer=result["answer"],
            context_used=result["context_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        chunks, doc_id = document_loader.load_and_chunk_document(tmp_path)

        stats = graph_builder.build_graph_from_chunks(chunks, doc_id)

        os.unlink(tmp_path)

        return {
            "doc_id": doc_id,
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        if 'tmp_path' in locals():
            os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ingest-batch")
async def ingest_batch(files: List[UploadFile] = File(...)):
    results = []
    overall_stats = {
        "total_documents": 0,
        "total_entities": 0,
        "total_relationships": 0
    }

    for file in files:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name

            chunks, doc_id = document_loader.load_and_chunk_document(tmp_path)
            stats = graph_builder.build_graph_from_chunks(chunks, doc_id)

            results.append({
                "filename": file.filename,
                "doc_id": doc_id,
                "status": "success",
                "stats": stats
            })

            overall_stats["total_documents"] += 1
            overall_stats["total_entities"] += stats["entities_extracted"]
            overall_stats["total_relationships"] += stats["relationships_extracted"]

            os.unlink(tmp_path)
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
            if 'tmp_path' in locals():
                os.unlink(tmp_path)

    return {
        "overall_stats": overall_stats,
        "file_results": results
    }

@app.get("/graph/stats")
async def graph_stats():
    summary = query_engine.get_graph_summary()
    return summary

@app.get("/graph/entity/{entity_id}")
async def get_entity(entity_id: str):
    context = query_engine.get_entity_context(entity_id, depth=2)
    return context

@app.get("/graph/search")
async def search_entities(q: str, entity_type: Optional[str] = None):
    results = query_engine.search_entities(q, entity_type)
    return {"query": q, "results": results}

@app.post("/graph/connections")
async def find_connections(entity1_id: str, entity2_id: str):
    connections = query_engine.find_connections(entity1_id, entity2_id)
    return connections

@app.delete("/graph/reset")
async def reset_graph():
    graph_db.delete_all()
    return {"status": "Graph cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
