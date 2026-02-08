from typing import List, Dict, Any, Tuple
from modules.utils import get_logger, QueryHelper

logger = get_logger(__name__)

class ContextRanker:
    def __init__(self):
        self.logger = get_logger(__name__)

    def rank_documents(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored_docs = []

        for doc in documents:
            score = self._calculate_document_score(query, doc)
            doc_copy = doc.copy()
            doc_copy["context_score"] = score
            scored_docs.append(doc_copy)

        return sorted(scored_docs, key=lambda x: x.get("context_score", 0), reverse=True)

    def _calculate_document_score(self, query: str, document: Dict[str, Any]) -> float:
        score = 0.0

        relevance_score = document.get("score", 0.5)
        score += relevance_score * 0.35

        content = document.get("metadata", {}).get("content", "")
        length_score = self._score_document_length(content)
        score += length_score * 0.25

        keyword_score = self._score_keyword_match(query, content)
        score += keyword_score * 0.20

        source_score = self._score_source_quality(document)
        score += source_score * 0.15

        recency_score = self._score_recency(document)
        score += recency_score * 0.05

        return min(score, 1.0)

    def _score_document_length(self, content: str) -> float:
        word_count = len(content.split())
        optimal_length = 200

        if word_count < 50:
            return 0.2
        elif word_count < optimal_length:
            return word_count / optimal_length
        elif word_count < 500:
            return 1.0
        else:
            return max(1.0 - (word_count - 500) / 1000, 0.5)

    def _score_keyword_match(self, query: str, content: str) -> float:
        keywords = QueryHelper.extract_keywords(query)
        if not keywords:
            return 0.5

        content_lower = content.lower()
        matched = sum(1 for kw in keywords if kw.lower() in content_lower)

        return matched / len(keywords) if keywords else 0.0

    def _score_source_quality(self, document: Dict[str, Any]) -> float:
        source = document.get("metadata", {}).get("source", "").lower()

        quality_sources = {
            "arxiv": 1.0,
            "nature": 1.0,
            "science": 1.0,
            "ieee": 0.95,
            "acm": 0.95,
            "github": 0.8,
            "stackoverflow": 0.75,
            "medium": 0.6,
            "blog": 0.5
        }

        for source_name, quality in quality_sources.items():
            if source_name in source:
                return quality

        return 0.4

    def _score_recency(self, document: Dict[str, Any]) -> float:
        from datetime import datetime, timedelta

        timestamp_str = document.get("metadata", {}).get("timestamp")

        if not timestamp_str:
            return 0.5

        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            days_old = (datetime.now() - timestamp).days

            if days_old <= 180:
                return 1.0
            elif days_old <= 365:
                return 0.7
            else:
                return 0.4
        except:
            return 0.5

    def select_top_k(self, query: str, documents: List[Dict[str, Any]], k: int = 5) -> List[Dict[str, Any]]:
        ranked = self.rank_documents(query, documents)
        return ranked[:k]

    def filter_by_threshold(self, query: str, documents: List[Dict[str, Any]],
                           threshold: float = 0.5) -> List[Dict[str, Any]]:
        ranked = self.rank_documents(query, documents)
        return [doc for doc in ranked if doc.get("context_score", 0) >= threshold]
