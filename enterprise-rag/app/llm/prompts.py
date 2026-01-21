from typing import Dict, Any, List, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.llm.models import PromptTemplate

logger = logging.getLogger(__name__)


SYSTEM_PROMPT_TEMPLATE = """You are an expert assistant for answering questions about enterprise documents and knowledge bases.

Instructions:
1. Answer questions based solely on the provided context
2. If the answer is not in the context, clearly state that
3. Provide accurate, concise, and helpful answers
4. Cite sources when referencing specific documents
5. Format your response clearly with proper structure

Context:
{context}

Answer the user's question based on the above context."""


RAG_PROMPT_TEMPLATE = """Based on the following retrieved documents, answer the user's question.

Retrieved Documents:
{retrieved_documents}

User Question: {question}

Please provide a comprehensive answer citing the relevant documents."""


SUMMARY_PROMPT_TEMPLATE = """Summarize the following documents in a concise manner:

Documents:
{documents}

Summary:"""


class PromptService:

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_template(self, name: str) -> Optional[PromptTemplate]:
        try:
            result = await self.db.execute(
                select(PromptTemplate).where(
                    (PromptTemplate.name == name) &
                    (PromptTemplate.is_active == True)
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Template retrieval error: {str(e)}")
            return None

    async def create_template(
        self,
        name: str,
        template: str,
        system_prompt: Optional[str] = None,
        variables: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> PromptTemplate:
        try:
            prompt_template = PromptTemplate(
                name=name,
                template=template,
                system_prompt=system_prompt,
                variables=variables or [],
                description=description
            )
            self.db.add(prompt_template)
            await self.db.flush()
            logger.info(f"Created prompt template: {name}")
            return prompt_template
        except Exception as e:
            logger.error(f"Template creation error: {str(e)}")
            raise

    async def format_prompt(
        self,
        template_name: str,
        **variables
    ) -> Dict[str, str]:
        try:
            template = await self.get_template(template_name)
            if not template:
                raise ValueError(f"Template {template_name} not found")

            formatted_template = template.template.format(**variables)
            system = template.system_prompt.format(**variables) if template.system_prompt else None

            return {
                "system": system,
                "prompt": formatted_template
            }
        except Exception as e:
            logger.error(f"Prompt formatting error: {str(e)}")
            raise

    @staticmethod
    def format_rag_prompt(
        question: str,
        context: List[str],
        system_prompt: Optional[str] = None
    ) -> Dict[str, str]:
        context_text = "\n\n".join(context)
        formatted_system = system_prompt or SYSTEM_PROMPT_TEMPLATE.format(context=context_text)

        return {
            "system": formatted_system,
            "user": question
        }

    @staticmethod
    def format_with_context(
        template: str,
        context: str,
        **kwargs
    ) -> str:
        try:
            return template.format(context=context, **kwargs)
        except Exception as e:
            logger.error(f"Template formatting error: {str(e)}")
            raise

    @staticmethod
    def add_citations(response: str, sources: List[Dict[str, Any]]) -> str:
        if not sources:
            return response

        citations = "\n\nSources:\n"
        for idx, source in enumerate(sources, 1):
            title = source.get("title", "Unknown")
            url = source.get("url", "")
            if url:
                citations += f"{idx}. {title} ({url})\n"
            else:
                citations += f"{idx}. {title}\n"

        return response + citations

    @staticmethod
    def extract_answer_from_response(response: str) -> str:
        lines = response.split("\n")
        answer_lines = []
        in_answer = False

        for line in lines:
            if "answer" in line.lower() or not in_answer:
                in_answer = True
            if "source" in line.lower() or "citation" in line.lower():
                break
            if in_answer:
                answer_lines.append(line)

        return "\n".join(answer_lines).strip()
