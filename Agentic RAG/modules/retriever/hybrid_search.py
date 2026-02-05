from typing import List, Dict, Any, Optional
from modules.utils import get_logger, QueryHelper

logger = get_logger(__name__)

class HybridSearch:
    def __init__(self,
                 semantic_searcher=None,
                 keyword_searcher=None,
                 semantic_weight: float = 0.7,
                 keyword_weight: float = 0.3):
        self.semantic_searcher = semantic_searcher
        self.keyword_searcher = keyword_searcher
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.logger = get_logger(__name__)

    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        semantic_results = []
        keyword_results = []

        if self.semantic_searcher:
            try:
                semantic_results = self.semantic_searcher.search(query, top_k=top_k * 2)
            except Exception as e:
                self.logger.warning(f"Semantic search failed: {e}")

        if self.keyword_searcher:
            try:
                keyword_results = self.keyword_searcher.search(query, top_k=top_k * 2)
            except Exception as e:
                self.logger.warning(f"Keyword search failed: {e}")

        combined_results = self._combine_results(
            semantic_results,
            keyword_results,
            top_k
        )

        filtered_results = [
            result for result in combined_results
            if result.get("score", 0) >= score_threshold
        ]

        self.logger.info(f"Hybrid search returned {len(filtered_results)} results")
        return filtered_results[:top_k]

    def _combine_results(self,
                        semantic_results: List[Dict[str, Any]],
                        keyword_results: List[Dict[str, Any]],
                        top_k: int) -> List[Dict[str, Any]]:
        merged = {}

        for result in semantic_results:
            result_id = result.get("id")
            if result_id:
                merged[result_id] = {
                    "id": result_id,
                    "semantic_score": result.get("score", 0),
                    "keyword_score": 0,
                    "metadata": result.get("metadata", {})
                }

        for result in keyword_results:
            result_id = result.get("id")
            if result_id:
                if result_id in merged:
                    merged[result_id]["keyword_score"] = result.get("score", 0)
                else:
                    merged[result_id] = {
                        "id": result_id,
                        "semantic_score": 0,
                        "keyword_score": result.get("score", 0),
                        "metadata": result.get("metadata", {})
                    }

        for result_id, data in merged.items():
            normalized_semantic = min(data["semantic_score"] / 1.0, 1.0) if data["semantic_score"] > 0 else 0
            normalized_keyword = min(data["keyword_score"] / 100.0, 1.0) if data["keyword_score"] > 0 else 0

            combined_score = (
                self.semantic_weight * normalized_semantic +
                self.keyword_weight * normalized_keyword
            )

            data["score"] = combined_score

        combined_list = list(merged.values())
        combined_list.sort(key=lambda x: x.get("score", 0), reverse=True)

        return combined_list[:top_k * 2]

    def search_with_strategy(self,
                            query: str,
                            strategy: str = "hybrid",
                            top_k: int = 5) -> List[Dict[str, Any]]:
        if strategy == "semantic" and self.semantic_searcher:
            return self.semantic_searcher.search(query, top_k=top_k)
        elif strategy == "keyword" and self.keyword_searcher:
            return self.keyword_searcher.search(query, top_k=top_k)
        else:
            return self.search(query, top_k=top_k)

    def adjust_weights(self, semantic_weight: float, keyword_weight: float):
        if semantic_weight + keyword_weight != 1.0:
            self.logger.warning("Weights don't sum to 1.0, normalizing")
            total = semantic_weight + keyword_weight
            semantic_weight /= total
            keyword_weight /= total

        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.logger.info(f"Adjusted weights - semantic: {semantic_weight}, keyword: {keyword_weight}")
