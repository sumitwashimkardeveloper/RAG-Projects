from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class RankingCriteria:
    name: str
    weight: float
    scorer: Callable[[Dict[str, Any]], float]

class RankingEngine:
    def __init__(self):
        self.criteria: List[RankingCriteria] = []
        self.logger = get_logger(__name__)

    def add_criteria(self, name: str, weight: float, scorer: Callable):
        self.criteria.append(RankingCriteria(name=name, weight=weight, scorer=scorer))
        self.logger.info(f"Added ranking criteria: {name} (weight: {weight})")

    def rank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.criteria:
            return sorted(results, key=lambda x: x.get("score", 0), reverse=True)

        scored_results = []
        for result in results:
            scores = {}
            total_score = 0

            for criteria in self.criteria:
                try:
                    score = criteria.scorer(result)
                    scores[criteria.name] = score
                    total_score += score * criteria.weight
                except Exception as e:
                    self.logger.warning(f"Error scoring with {criteria.name}: {e}")
                    scores[criteria.name] = 0

            result["ranking_scores"] = scores
            result["combined_score"] = total_score

            scored_results.append(result)

        scored_results.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
        return scored_results

    def reset_criteria(self):
        self.criteria = []
        self.logger.info("Reset all ranking criteria")

class ScoreNormalizer:
    @staticmethod
    def normalize_minmax(results: List[Dict[str, Any]], key: str = "score") -> List[Dict[str, Any]]:
        if not results:
            return results

        scores = [r.get(key, 0) for r in results]
        min_score = min(scores) if scores else 0
        max_score = max(scores) if scores else 1
        score_range = max_score - min_score if max_score > min_score else 1

        normalized = []
        for result in results:
            score = result.get(key, 0)
            normalized_score = (score - min_score) / score_range if score_range > 0 else 0.5
            result["normalized_score"] = normalized_score
            normalized.append(result)

        return normalized

    @staticmethod
    def normalize_zscore(results: List[Dict[str, Any]], key: str = "score") -> List[Dict[str, Any]]:
        if not results:
            return results

        scores = [r.get(key, 0) for r in results]
        mean = sum(scores) / len(scores) if scores else 0
        variance = sum((s - mean) ** 2 for s in scores) / len(scores) if scores else 0
        std_dev = variance ** 0.5 if variance > 0 else 1

        normalized = []
        for result in results:
            score = result.get(key, 0)
            z_score = (score - mean) / std_dev if std_dev > 0 else 0
            result["z_score"] = z_score
            normalized.append(result)

        return normalized

class ResultScorer:
    @staticmethod
    def score_relevance(result: Dict[str, Any], query_keywords: List[str]) -> float:
        content = result.get("metadata", {}).get("content", "").lower()
        matched = sum(1 for kw in query_keywords if kw.lower() in content)
        return matched / len(query_keywords) if query_keywords else 0

    @staticmethod
    def score_recency(result: Dict[str, Any]) -> float:
        timestamp = result.get("metadata", {}).get("timestamp")
        if not timestamp:
            return 0.5

        from datetime import datetime
        try:
            created_at = datetime.fromisoformat(timestamp)
            days_old = (datetime.now() - created_at).days
            return max(0, 1 - (days_old / 365))
        except:
            return 0.5

    @staticmethod
    def score_length(result: Dict[str, Any]) -> float:
        content = result.get("metadata", {}).get("content", "")
        length = len(content.split())
        optimal_length = 100

        if length == 0:
            return 0
        if length < optimal_length:
            return length / optimal_length
        else:
            return optimal_length / length

    @staticmethod
    def score_authority(result: Dict[str, Any]) -> float:
        source = result.get("metadata", {}).get("source", "").lower()

        authority_sources = ["arxiv", "nature", "science", "ieee", "acm", "nih"]
        for source_name in authority_sources:
            if source_name in source:
                return 0.9

        citation_count = result.get("metadata", {}).get("citations", 0)
        if isinstance(citation_count, int):
            return min(citation_count / 100, 1.0)

        return 0.5
