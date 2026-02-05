from typing import List, Dict, Any, Tuple
from modules.utils import get_logger

logger = get_logger(__name__)

class CompletenessChecker:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.min_content_length = 100
        self.min_doc_count = 2
        self.min_coverage = 0.6

    def check(self, query: str, documents: List[Dict[str, Any]]) -> Tuple[bool, float]:
        if not documents:
            return False, 0.0

        completeness_score = self._calculate_completeness(query, documents)
        is_complete = completeness_score >= 0.7

        self.logger.info(f"Completeness check: {is_complete} (score: {completeness_score:.2f})")
        return is_complete, completeness_score

    def _calculate_completeness(self, query: str, documents: List[Dict[str, Any]]) -> float:
        score = 0.0

        doc_count_score = self._document_count_score(len(documents))
        score += doc_count_score * 0.25

        content_quality_score = self._content_quality_score(documents)
        score += content_quality_score * 0.3

        coverage_score = self._query_coverage_score(query, documents)
        score += coverage_score * 0.25

        diversity_score = self._diversity_score(documents)
        score += diversity_score * 0.2

        return min(score, 1.0)

    def _document_count_score(self, doc_count: int) -> float:
        if doc_count == 0:
            return 0.0
        elif doc_count < 2:
            return 0.4
        elif doc_count < 5:
            return 0.7
        elif doc_count < 10:
            return 0.9
        else:
            return 1.0

    def _content_quality_score(self, documents: List[Dict[str, Any]]) -> float:
        if not documents:
            return 0.0

        quality_scores = []

        for doc in documents:
            content = doc.get("metadata", {}).get("content", "")
            content_length = len(content.split())

            if content_length < self.min_content_length:
                quality_scores.append(0.4)
            elif content_length < 500:
                quality_scores.append(0.7)
            else:
                quality_scores.append(1.0)

        return sum(quality_scores) / len(quality_scores)

    def _query_coverage_score(self, query: str, documents: List[Dict[str, Any]]) -> float:
        if not query or not documents:
            return 0.0

        query_words = set(query.lower().split())
        combined_content = " ".join(
            doc.get("metadata", {}).get("content", "").lower()
            for doc in documents
        )

        matched_words = sum(1 for word in query_words if word in combined_content)
        coverage = matched_words / len(query_words) if query_words else 0.0

        return min(coverage, 1.0)

    def _diversity_score(self, documents: List[Dict[str, Any]]) -> float:
        if len(documents) < 2:
            return 0.5

        sources = set()
        for doc in documents:
            source = doc.get("metadata", {}).get("source", "unknown")
            sources.add(source)

        diversity = len(sources) / len(documents)
        return min(diversity, 1.0)

    def get_completeness_report(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        is_complete, score = self.check(query, documents)

        doc_count = len(documents)
        content_quality = self._content_quality_score(documents)
        coverage = self._query_coverage_score(query, documents)
        diversity = self._diversity_score(documents)

        return {
            "is_complete": is_complete,
            "completeness_score": score,
            "document_count": doc_count,
            "content_quality": content_quality,
            "query_coverage": coverage,
            "source_diversity": diversity,
            "suggestions": self._generate_suggestions(is_complete, score, doc_count, coverage)
        }

    def _generate_suggestions(self, is_complete: bool, score: float, doc_count: int, coverage: float) -> List[str]:
        suggestions = []

        if not is_complete:
            if score < 0.3:
                suggestions.append("Very low completeness. Consider reformulating the query.")
                suggestions.append("Increase the number of retrieved documents.")

            if doc_count < 3:
                suggestions.append("Increase the number of documents to improve completeness.")

            if coverage < 0.5:
                suggestions.append("Query keywords are not well covered. Reformulate the query.")

            if coverage < 0.3:
                suggestions.append("Consider searching for related terms or concepts.")

        return suggestions

    def needs_more_info(self, query: str, documents: List[Dict[str, Any]]) -> bool:
        _, score = self.check(query, documents)
        return score < 0.7

    def is_satisfactory(self, query: str, documents: List[Dict[str, Any]], threshold: float = 0.8) -> bool:
        _, score = self.check(query, documents)
        return score >= threshold
