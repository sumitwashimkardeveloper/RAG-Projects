from typing import List, Dict, Any, Tuple
from modules.utils import get_logger, QueryHelper

logger = get_logger(__name__)

class RelevanceEvaluator:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.relevance_keywords = {
            "high": ["directly", "exactly", "precisely", "matches", "answers"],
            "medium": ["relates", "connected", "similar", "relevant", "similar"],
            "low": ["tangential", "vague", "indirect", "loosely"]
        }

    def evaluate(self, query: str, document: Dict[str, Any]) -> Tuple[bool, float]:
        is_relevant, score = self._calculate_relevance_score(query, document)
        self.logger.info(f"Relevance evaluation: {is_relevant} (score: {score:.2f})")
        return is_relevant, score

    def _calculate_relevance_score(self, query: str, document: Dict[str, Any]) -> Tuple[bool, float]:
        content = document.get("metadata", {}).get("content", "").lower()
        query_lower = query.lower()

        score = 0.0

        query_words = set(QueryHelper.extract_keywords(query))
        matched_words = sum(1 for word in query_words if word.lower() in content)
        word_match_score = matched_words / len(query_words) if query_words else 0
        score += word_match_score * 0.4

        if query_lower in content:
            score += 0.3

        doc_length = len(content.split())
        if doc_length > 50:
            score += 0.15
        elif doc_length > 20:
            score += 0.1

        entity_score = self._entity_match_score(query, content)
        score += entity_score * 0.15

        is_relevant = score >= 0.4
        final_score = min(score, 1.0)

        return is_relevant, final_score

    def _entity_match_score(self, query: str, content: str) -> float:
        capitalized_words = [word for word in query.split() if word[0].isupper()]
        if not capitalized_words:
            return 0.0

        matched = sum(1 for word in capitalized_words if word in content)
        return matched / len(capitalized_words) if capitalized_words else 0.0

    def evaluate_batch(self, query: str, documents: List[Dict[str, Any]]) -> List[Tuple[bool, float]]:
        results = []
        for doc in documents:
            is_relevant, score = self.evaluate(query, doc)
            results.append((is_relevant, score))
        return results

    def find_most_relevant(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not documents:
            return {}

        scores = []
        for doc in documents:
            _, score = self.evaluate(query, doc)
            scores.append(score)

        max_idx = scores.index(max(scores))
        return documents[max_idx]

    def filter_by_relevance(self, query: str, documents: List[Dict[str, Any]],
                           threshold: float = 0.4) -> List[Dict[str, Any]]:
        relevant = []
        for doc in documents:
            is_relevant, score = self.evaluate(query, doc)
            if is_relevant and score >= threshold:
                doc["relevance_score"] = score
                relevant.append(doc)

        return sorted(relevant, key=lambda x: x.get("relevance_score", 0), reverse=True)
