from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class Citation:
    source: str
    content_snippet: str
    relevance_score: float
    page_number: int = 0
    sentence_range: Tuple[int, int] = (0, 0)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CitationTracker:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.citations: List[Citation] = []

    def extract_citations(self, answer: str, documents: List[Dict[str, Any]]) -> List[Citation]:
        citations = []

        for doc in documents:
            content = doc.get("metadata", {}).get("content", "")
            source = doc.get("metadata", {}).get("source", "unknown")
            score = doc.get("score", doc.get("context_score", 0.5))

            sentences = self._extract_relevant_sentences(answer, content)

            for sentence in sentences[:2]:
                citation = Citation(
                    source=source,
                    content_snippet=sentence,
                    relevance_score=score,
                    metadata={
                        "document_id": doc.get("id", "unknown"),
                        "sentence_index": sentences.index(sentence)
                    }
                )
                citations.append(citation)

        self.citations = citations
        self.logger.info(f"Extracted {len(citations)} citations")
        return citations

    def _extract_relevant_sentences(self, answer: str, content: str) -> List[str]:
        content_sentences = [s.strip() for s in content.split('.') if s.strip()]
        answer_words = set(answer.lower().split())

        relevant_sentences = []

        for sentence in content_sentences:
            sentence_words = set(sentence.lower().split())
            overlap = len(answer_words & sentence_words)

            if overlap > 0:
                relevant_sentences.append(sentence + ".")

        return relevant_sentences[:3]

    def create_citation_list(self, citations: List[Citation] = None) -> List[Dict[str, Any]]:
        if citations is None:
            citations = self.citations

        citation_list = []
        seen_sources = set()

        for i, citation in enumerate(citations, 1):
            if citation.source not in seen_sources:
                citation_list.append({
                    "number": i,
                    "source": citation.source,
                    "snippet": citation.content_snippet[:100],
                    "relevance": citation.relevance_score
                })
                seen_sources.add(citation.source)

        return citation_list

    def format_citations_markdown(self, citations: List[Citation] = None) -> str:
        if citations is None:
            citations = self.citations

        if not citations:
            return ""

        lines = ["## Sources\n"]
        seen_sources = {}

        for citation in citations:
            source = citation.source
            if source not in seen_sources:
                seen_sources[source] = len(seen_sources) + 1

        for source, number in sorted(seen_sources.items(), key=lambda x: x[1]):
            lines.append(f"{number}. {source}")

        return "\n".join(lines)

    def get_citation_mapping(self, answer: str, citations: List[Citation] = None) -> Dict[str, List[int]]:
        if citations is None:
            citations = self.citations

        answer_lower = answer.lower()
        citation_map = {}

        for i, citation in enumerate(citations, 1):
            snippet_lower = citation.content_snippet.lower()

            if snippet_lower in answer_lower:
                key = citation.source
                if key not in citation_map:
                    citation_map[key] = []
                citation_map[key].append(i)

        return citation_map

    def validate_citations(self, citations: List[Citation] = None) -> Dict[str, Any]:
        if citations is None:
            citations = self.citations

        total_citations = len(citations)
        unique_sources = len(set(c.source for c in citations))
        avg_relevance = sum(c.relevance_score for c in citations) / len(citations) if citations else 0

        high_relevance = sum(1 for c in citations if c.relevance_score >= 0.7)

        return {
            "total_citations": total_citations,
            "unique_sources": unique_sources,
            "average_relevance": avg_relevance,
            "high_relevance_count": high_relevance,
            "high_relevance_percentage": (high_relevance / total_citations * 100) if total_citations > 0 else 0
        }

    def get_top_citations(self, k: int = 5) -> List[Citation]:
        sorted_citations = sorted(self.citations, key=lambda x: x.relevance_score, reverse=True)
        return sorted_citations[:k]

    def clear_citations(self):
        self.citations = []
        self.logger.info("Cleared citations")
