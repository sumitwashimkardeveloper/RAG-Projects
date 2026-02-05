from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from modules.utils import get_logger

logger = get_logger(__name__)

class ConfidenceScorer:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.base_threshold = 0.5

    def score(self, documents: List[Dict[str, Any]], query: str = "") -> float:
        if not documents:
            return 0.0

        confidence_scores = []

        for doc in documents:
            score = self._calculate_confidence(doc, query)
            confidence_scores.append(score)

        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        final_confidence = min(avg_confidence, 1.0)

        self.logger.info(f"Confidence score: {final_confidence:.2f}")
        return final_confidence

    def _calculate_confidence(self, document: Dict[str, Any], query: str = "") -> float:
        score = 0.0

        retrieval_score = document.get("score", 0)
        score += min(retrieval_score, 1.0) * 0.3

        doc_score = document.get("relevance_score", 0.5)
        score += min(doc_score, 1.0) * 0.25

        source_confidence = self._source_confidence(document)
        score += source_confidence * 0.2

        recency_score = self._recency_score(document)
        score += recency_score * 0.15

        consistency_score = self._consistency_score(document, query)
        score += consistency_score * 0.1

        return min(score, 1.0)

    def _source_confidence(self, document: Dict[str, Any]) -> float:
        source = document.get("metadata", {}).get("source", "").lower()

        authoritative_sources = {
            "arxiv": 0.95,
            "nature": 0.95,
            "science": 0.95,
            "ieee": 0.9,
            "acm": 0.9,
            "github": 0.85,
            "wikipedia": 0.7,
            "medium": 0.6,
            "blog": 0.5,
            "unknown": 0.3
        }

        for source_name, confidence in authoritative_sources.items():
            if source_name in source:
                return confidence

        return 0.4

    def _recency_score(self, document: Dict[str, Any]) -> float:
        timestamp_str = document.get("metadata", {}).get("timestamp")

        if not timestamp_str:
            return 0.5

        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            days_old = (datetime.now() - timestamp).days

            if days_old <= 30:
                return 1.0
            elif days_old <= 365:
                return max(1.0 - (days_old / 730), 0.3)
            else:
                return 0.2
        except:
            return 0.5

    def _consistency_score(self, document: Dict[str, Any], query: str = "") -> float:
        if not query:
            return 0.5

        content = document.get("metadata", {}).get("content", "").lower()
        query_lower = query.lower()

        contradictory_words = ["not", "no", "never", "false"]
        contradictions = sum(1 for word in contradictory_words if word in content and word in query_lower)

        if contradictions > 0:
            return 0.2

        return 0.8

    def score_distribution(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not documents:
            return {"mean": 0, "min": 0, "max": 0, "std_dev": 0}

        scores = [self._calculate_confidence(doc) for doc in documents]

        mean = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5

        return {
            "mean": mean,
            "min": min_score,
            "max": max_score,
            "std_dev": std_dev,
            "count": len(scores)
        }

    def is_confident(self, documents: List[Dict[str, Any]], threshold: float = 0.6) -> bool:
        confidence = self.score(documents)
        return confidence >= threshold
