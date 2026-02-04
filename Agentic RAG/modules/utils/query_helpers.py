from typing import List, Dict, Any, Optional, Tuple
from modules.utils import get_logger

logger = get_logger(__name__)

class QueryHelper:
    @staticmethod
    def normalize_query(query: str) -> str:
        query = query.strip()
        query = " ".join(query.split())
        return query.lower()

    @staticmethod
    def extract_keywords(query: str) -> List[str]:
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "from", "is", "was",
            "are", "were", "be", "been", "being", "has", "have", "had"
        }

        words = QueryHelper.normalize_query(query).split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords

    @staticmethod
    def split_query(query: str, delimiter: str = " ") -> List[str]:
        parts = query.split(delimiter)
        return [p.strip() for p in parts if p.strip()]

    @staticmethod
    def build_filter(metadata_filters: Dict[str, Any]) -> Dict[str, Any]:
        filter_dict = {}

        for key, value in metadata_filters.items():
            if isinstance(value, str):
                filter_dict[key] = {"$eq": value}
            elif isinstance(value, (int, float)):
                filter_dict[key] = {"$eq": value}
            elif isinstance(value, list):
                filter_dict[key] = {"$in": value}
            elif isinstance(value, dict):
                filter_dict[key] = value

        return filter_dict

    @staticmethod
    def merge_results(result_lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        merged = {}

        for results in result_lists:
            for result in results:
                result_id = result.get("id")
                if result_id in merged:
                    merged[result_id]["score"] = max(
                        merged[result_id].get("score", 0),
                        result.get("score", 0)
                    )
                else:
                    merged[result_id] = result

        return sorted(
            merged.values(),
            key=lambda x: x.get("score", 0),
            reverse=True
        )

    @staticmethod
    def deduplicate_results(results: List[Dict[str, Any]], key: str = "id") -> List[Dict[str, Any]]:
        seen = set()
        deduplicated = []

        for result in results:
            result_key = result.get(key)
            if result_key and result_key not in seen:
                seen.add(result_key)
                deduplicated.append(result)

        return deduplicated

    @staticmethod
    def filter_by_score(results: List[Dict[str, Any]], threshold: float) -> List[Dict[str, Any]]:
        return [r for r in results if r.get("score", 0) >= threshold]

    @staticmethod
    def limit_results(results: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        return results[:limit]

    @staticmethod
    def sort_results(results: List[Dict[str, Any]], key: str = "score", reverse: bool = True) -> List[Dict[str, Any]]:
        return sorted(results, key=lambda x: x.get(key, 0), reverse=reverse)
