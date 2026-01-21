from typing import List, Dict, Any, Optional, AsyncIterator
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.llm.base import BaseLLMProvider
from app.llm.models import QueryResponse, ResponseFeedback
from app.llm.prompts import PromptService
from app.retrieval.hybrid import HybridRetriever
from app.embeddings.service import EmbeddingService

logger = logging.getLogger(__name__)


class LLMService:

    def __init__(
        self,
        db_session: AsyncSession,
        llm_provider: BaseLLMProvider,
        retriever: Optional[HybridRetriever] = None
    ):
        self.db = db_session
        self.llm = llm_provider
        self.retriever = retriever
        self.prompt_service = PromptService(db_session)

    async def answer_question(
        self,
        question: str,
        top_k: int = 10,
        use_context: bool = True,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            sources = []
            context = []

            if use_context and self.retriever:
                results = await self.retriever.retrieve(question, top_k=top_k)
                context = [r.get("content", "") for r in results if r.get("content")]
                sources = results

            messages = self.llm.format_messages(
                system_prompt=system_prompt,
                user_query=question,
                context=context
            )

            response = await self.llm.generate_async(messages)

            input_tokens = sum(self.llm.count_tokens(m.get("content", "")) for m in messages)
            output_tokens = self.llm.count_tokens(response)

            query_response = QueryResponse(
                query=question,
                response=response,
                model=self.llm.model,
                provider="openai" if "gpt" in self.llm.model else "anthropic",
                tokens_input=input_tokens,
                tokens_output=output_tokens,
                retrieved_chunks=len(context),
                sources=[{"chunk_id": s.get("chunk_id"), "score": s.get("score")} for s in sources],
                has_citation=len(sources) > 0
            )

            self.db.add(query_response)
            await self.db.flush()

            return {
                "response_id": str(query_response.id),
                "answer": response,
                "sources": sources,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens
                },
                "model": self.llm.model
            }

        except Exception as e:
            logger.error(f"Question answering error: {str(e)}")
            raise

    async def stream_answer(
        self,
        question: str,
        top_k: int = 10,
        use_context: bool = True,
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        try:
            context = []

            if use_context and self.retriever:
                results = await self.retriever.retrieve(question, top_k=top_k)
                context = [r.get("content", "") for r in results if r.get("content")]

            messages = self.llm.format_messages(
                system_prompt=system_prompt,
                user_query=question,
                context=context
            )

            async for chunk in self.llm.stream(messages):
                yield chunk

        except Exception as e:
            logger.error(f"Stream answer error: {str(e)}")
            raise

    async def summarize(
        self,
        text: str,
        max_length: Optional[int] = None
    ) -> str:
        try:
            system_prompt = "You are an expert summarizer. Provide a clear and concise summary."
            if max_length:
                system_prompt += f"\nKeep the summary to approximately {max_length} words."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please summarize the following text:\n\n{text}"}
            ]

            response = await self.llm.generate_async(messages)
            return response

        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            raise

    async def extract_key_points(
        self,
        text: str,
        num_points: int = 5
    ) -> List[str]:
        try:
            system_prompt = f"Extract the {num_points} key points from the following text."

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Text:\n\n{text}"}
            ]

            response = await self.llm.generate_async(messages)

            points = [p.strip() for p in response.split("\n") if p.strip()]
            return points[:num_points]

        except Exception as e:
            logger.error(f"Key extraction error: {str(e)}")
            raise

    async def evaluate_response(
        self,
        response_id: str,
        rating: Optional[int] = None,
        helpful: Optional[bool] = None,
        accurate: Optional[bool] = None,
        complete: Optional[bool] = None,
        comments: Optional[str] = None
    ) -> bool:
        try:
            feedback = ResponseFeedback(
                response_id=response_id,
                rating=rating,
                helpful=helpful,
                accurate=accurate,
                complete=complete,
                comments=comments
            )
            self.db.add(feedback)
            await self.db.flush()
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Feedback error: {str(e)}")
            await self.db.rollback()
            return False

    async def get_response_quality_stats(self) -> Dict[str, Any]:
        try:
            result = await self.db.execute(select(ResponseFeedback))
            feedbacks = result.scalars().all()

            if not feedbacks:
                return {"total_feedbacks": 0}

            helpful_count = sum(1 for f in feedbacks if f.helpful)
            accurate_count = sum(1 for f in feedbacks if f.accurate)
            complete_count = sum(1 for f in feedbacks if f.complete)

            avg_rating = sum(f.rating for f in feedbacks if f.rating) / len([f for f in feedbacks if f.rating]) if any(f.rating for f in feedbacks) else 0

            return {
                "total_feedbacks": len(feedbacks),
                "avg_rating": avg_rating,
                "helpful_percentage": (helpful_count / len(feedbacks) * 100) if feedbacks else 0,
                "accurate_percentage": (accurate_count / len(feedbacks) * 100) if feedbacks else 0,
                "complete_percentage": (complete_count / len(feedbacks) * 100) if feedbacks else 0
            }
        except Exception as e:
            logger.error(f"Stats error: {str(e)}")
            return {}
