from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from modules.utils import get_logger
from .context_ranker import ContextRanker
from .prompt_templates import PromptTemplateManager
from .response_synthesizer import ResponseSynthesizer
from .citation_tracker import CitationTracker, Citation
from .answer_validator import AnswerValidator

logger = get_logger(__name__)

@dataclass
class GeneratedAnswer:
    query: str
    answer: str
    citations: List[Citation] = field(default_factory=list)
    confidence_score: float = 0.0
    validation_score: float = 0.0
    validation_issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AnswerGenerator:
    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)

        self.context_ranker = ContextRanker()
        self.prompt_manager = PromptTemplateManager()
        self.synthesizer = ResponseSynthesizer()
        self.citation_tracker = CitationTracker()
        self.validator = AnswerValidator()

    def generate(self, query: str, documents: List[Dict[str, Any]], context: Dict[str, Any] = None) -> GeneratedAnswer:
        self.logger.info(f"Generating answer for query: {query[:100]}")

        if not documents:
            return self._create_empty_answer(query)

        ranked_docs = self.rank_context(documents, query)
        selected_docs = self.select_relevant_docs(ranked_docs, query)

        context_text, sources = self.synthesizer.synthesize(query, selected_docs)

        intent = context.get("intent", "") if context else ""
        template_name = self.prompt_manager.select_template(intent)
        prompt = self.prompt_manager.format_prompt(query, context_text, template_name)

        answer_text = self._call_llm(prompt)

        citations = self.citation_tracker.extract_citations(answer_text, selected_docs)

        is_valid, validation_score, issues = self.validator.validate(answer_text, query, selected_docs)

        confidence = self._calculate_confidence(selected_docs, is_valid, validation_score)

        result = GeneratedAnswer(
            query=query,
            answer=answer_text,
            citations=citations,
            confidence_score=confidence,
            validation_score=validation_score,
            validation_issues=issues,
            metadata={
                "template_used": template_name,
                "documents_used": len(selected_docs),
                "is_valid": is_valid,
                "sources": sources
            }
        )

        self.logger.info(f"Generated answer with confidence {confidence:.2f}")
        return result

    def rank_context(self, documents: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        return self.context_ranker.rank_documents(query, documents)

    def select_relevant_docs(self, documents: List[Dict[str, Any]], query: str, max_count: int = 5) -> List[Dict[str, Any]]:
        return self.context_ranker.select_top_k(query, documents, k=max_count)

    def synthesize_response(self, query: str, documents: List[Dict[str, Any]]) -> str:
        context, _ = self.synthesizer.synthesize(query, documents)
        return context

    def extract_citations(self, answer: str, documents: List[Dict[str, Any]]) -> List[Citation]:
        return self.citation_tracker.extract_citations(answer, documents)

    def validate_answer(self, answer: str, query: str, documents: List[Dict[str, Any]] = None) -> Tuple[bool, float, List[str]]:
        return self.validator.validate(answer, query, documents)

    def _create_empty_answer(self, query: str) -> GeneratedAnswer:
        return GeneratedAnswer(
            query=query,
            answer="I was unable to find relevant documents to answer your question.",
            citations=[],
            confidence_score=0.0,
            validation_score=0.0,
            validation_issues=["No documents provided"]
        )

    def _call_llm(self, prompt: str) -> str:
        try:
            from anthropic import Anthropic
            client = Anthropic()

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return message.content[0].text
        except Exception as e:
            self.logger.error(f"Error calling LLM: {e}")
            return "Unable to generate answer due to an error."

    def _calculate_confidence(self, documents: List[Dict[str, Any]], is_valid: bool, validation_score: float) -> float:
        if not documents:
            return 0.0

        doc_confidence = sum(doc.get("context_score", doc.get("score", 0.5)) for doc in documents) / len(documents)

        validation_weight = 0.7 if is_valid else 0.3
        confidence = (doc_confidence * 0.6) + (validation_score * validation_weight)

        return min(confidence, 1.0)

    def format_answer_with_citations(self, answer: GeneratedAnswer) -> str:
        lines = [answer.answer, ""]

        if answer.citations:
            lines.append("\n## Sources")
            for i, citation in enumerate(answer.citations[:5], 1):
                lines.append(f"{i}. {citation.source}")

        return "\n".join(lines)

    def get_quality_report(self, answer: GeneratedAnswer) -> Dict[str, Any]:
        breakdown = self.validator.get_quality_score_breakdown(
            answer.answer,
            answer.query
        )

        return {
            "overall_confidence": answer.confidence_score,
            "validation_score": answer.validation_score,
            "quality_breakdown": breakdown,
            "is_valid": len(answer.validation_issues) < 3,
            "issues": answer.validation_issues,
            "citation_count": len(answer.citations)
        }
