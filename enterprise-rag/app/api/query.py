from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.llm import LLMService, OpenAILLMProvider, AnthropicLLMProvider
from app.retrieval import HybridRetriever
from app.embeddings import EmbeddingService, PineconeVectorStore
from app.config import settings

router = APIRouter(prefix="/api/v1/query", tags=["Query"])


class QueryRequest(BaseModel):
    question: str
    top_k: int = 10
    use_context: bool = True
    provider: str = "openai"
    system_prompt: Optional[str] = None


class StreamQueryRequest(BaseModel):
    question: str
    top_k: int = 10
    use_context: bool = True
    provider: str = "openai"


class FeedbackRequest(BaseModel):
    response_id: str
    rating: Optional[int] = None
    helpful: Optional[bool] = None
    accurate: Optional[bool] = None
    complete: Optional[bool] = None
    comments: Optional[str] = None


class SummarizeRequest(BaseModel):
    text: str
    max_length: Optional[int] = None


class KeyPointsRequest(BaseModel):
    text: str
    num_points: int = 5


@router.post("/ask")
async def ask_question(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        if request.provider == "openai":
            llm = OpenAILLMProvider()
        elif request.provider == "anthropic":
            llm = AnthropicLLMProvider()
        else:
            raise HTTPException(status_code=400, detail="Unknown provider")

        embedding_service = None
        retriever = None

        if request.use_context:
            provider = OpenAILLMProvider()
            vector_store = PineconeVectorStore()
            if vector_store.connect():
                embedding_service = EmbeddingService(db, provider, vector_store)
                retriever = HybridRetriever(db, embedding_service)

        service = LLMService(db, llm, retriever)
        result = await service.answer_question(
            request.question,
            top_k=request.top_k,
            use_context=request.use_context,
            system_prompt=request.system_prompt
        )

        await db.commit()
        return result

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_question(
    request: StreamQueryRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        if request.provider == "openai":
            llm = OpenAILLMProvider()
        elif request.provider == "anthropic":
            llm = AnthropicLLMProvider()
        else:
            raise HTTPException(status_code=400, detail="Unknown provider")

        retriever = None

        if request.use_context:
            provider = OpenAILLMProvider()
            vector_store = PineconeVectorStore()
            if vector_store.connect():
                embedding_service = EmbeddingService(db, provider, vector_store)
                retriever = HybridRetriever(db, embedding_service)

        service = LLMService(db, llm, retriever)

        async def generate():
            async for chunk in service.stream_answer(
                request.question,
                top_k=request.top_k,
                use_context=request.use_context
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/event-stream")

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def summarize_text(
    request: SummarizeRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        llm = OpenAILLMProvider()
        service = LLMService(db, llm)

        summary = await service.summarize(
            request.text,
            max_length=request.max_length
        )

        return {
            "original_length": len(request.text),
            "summary": summary,
            "summary_length": len(summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-keypoints")
async def extract_key_points(
    request: KeyPointsRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        llm = OpenAILLMProvider()
        service = LLMService(db, llm)

        points = await service.extract_key_points(
            request.text,
            num_points=request.num_points
        )

        return {
            "key_points": points,
            "count": len(points)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        llm = OpenAILLMProvider()
        service = LLMService(db, llm)

        success = await service.evaluate_response(
            request.response_id,
            rating=request.rating,
            helpful=request.helpful,
            accurate=request.accurate,
            complete=request.complete,
            comments=request.comments
        )

        if success:
            return {"status": "success", "message": "Feedback recorded"}
        else:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality-stats")
async def get_quality_stats(db: AsyncSession = Depends(get_db)):
    try:
        llm = OpenAILLMProvider()
        service = LLMService(db, llm)
        stats = await service.get_response_quality_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
