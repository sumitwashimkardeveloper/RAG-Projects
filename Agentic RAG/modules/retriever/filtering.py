from typing import List, Dict, Any, Callable, Optional, Set
from modules.utils import get_logger

logger = get_logger(__name__)

class Deduplicator:
    @staticmethod
    def deduplicate_by_id(results: List[Dict[str, Any]], id_key: str = "id") -> List[Dict[str, Any]]:
        seen = set()
        deduplicated = []

        for result in results:
            result_id = result.get(id_key)
            if result_id and result_id not in seen:
                seen.add(result_id)
                deduplicated.append(result)

        logger.info(f"Deduplicated {len(results)} results to {len(deduplicated)}")
        return deduplicated

    @staticmethod
    def deduplicate_by_content(results: List[Dict[str, Any]], content_key: str = "content") -> List[Dict[str, Any]]:
        seen_content = set()
        deduplicated = []

        for result in results:
            content = result.get("metadata", {}).get(content_key, "")
            content_hash = hash(content)

            if content_hash not in seen_content:
                seen_content.add(content_hash)
                deduplicated.append(result)

        logger.info(f"Deduplicated {len(results)} results to {len(deduplicated)} by content")
        return deduplicated

    @staticmethod
    def deduplicate_by_similarity(results: List[Dict[str, Any]],
                                 similarity_threshold: float = 0.9) -> List[Dict[str, Any]]:
        if not results:
            return results

        deduplicated = [results[0]]

        for current in results[1:]:
            is_duplicate = False

            for kept in deduplicated:
                similarity = Deduplicator._calculate_similarity(
                    current.get("metadata", {}).get("content", ""),
                    kept.get("metadata", {}).get("content", "")
                )

                if similarity > similarity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(current)

        logger.info(f"Deduplicated {len(results)} results to {len(deduplicated)} by similarity")
        return deduplicated

    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

class ResultFilter:
    @staticmethod
    def filter_by_score(results: List[Dict[str, Any]],
                       threshold: float,
                       score_key: str = "score") -> List[Dict[str, Any]]:
        filtered = [r for r in results if r.get(score_key, 0) >= threshold]
        logger.info(f"Filtered {len(results)} results by score threshold {threshold}: {len(filtered)} remain")
        return filtered

    @staticmethod
    def filter_by_metadata(results: List[Dict[str, Any]],
                          filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        filtered = []

        for result in results:
            metadata = result.get("metadata", {})
            match = True

            for key, value in filters.items():
                if isinstance(value, (list, tuple)):
                    if metadata.get(key) not in value:
                        match = False
                        break
                else:
                    if metadata.get(key) != value:
                        match = False
                        break

            if match:
                filtered.append(result)

        logger.info(f"Filtered {len(results)} results by metadata: {len(filtered)} remain")
        return filtered

    @staticmethod
    def filter_by_length(results: List[Dict[str, Any]],
                        min_length: int = 0,
                        max_length: int = None) -> List[Dict[str, Any]]:
        filtered = []

        for result in results:
            content = result.get("metadata", {}).get("content", "")
            content_length = len(content.split())

            if content_length >= min_length:
                if max_length is None or content_length <= max_length:
                    filtered.append(result)

        logger.info(f"Filtered {len(results)} results by length: {len(filtered)} remain")
        return filtered

    @staticmethod
    def filter_by_source(results: List[Dict[str, Any]],
                        allowed_sources: List[str]) -> List[Dict[str, Any]]:
        filtered = []

        for result in results:
            source = result.get("metadata", {}).get("source", "")
            if any(allowed in source for allowed in allowed_sources):
                filtered.append(result)

        logger.info(f"Filtered {len(results)} results by source: {len(filtered)} remain")
        return filtered

    @staticmethod
    def filter_by_custom(results: List[Dict[str, Any]],
                        predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        filtered = [r for r in results if predicate(r)]
        logger.info(f"Filtered {len(results)} results by custom predicate: {len(filtered)} remain")
        return filtered

class FilterPipeline:
    def __init__(self):
        self.filters = []

    def add_filter(self, name: str, filter_func: Callable):
        self.filters.append((name, filter_func))
        logger.info(f"Added filter: {name}")

    def apply(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        current = results
        for name, filter_func in self.filters:
            try:
                current = filter_func(current)
                logger.info(f"Applied filter '{name}': {len(current)} results remain")
            except Exception as e:
                logger.error(f"Error applying filter '{name}': {e}")

        return current

    def reset(self):
        self.filters = []
        logger.info("Reset filter pipeline")
