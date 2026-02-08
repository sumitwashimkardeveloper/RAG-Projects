from typing import List, Dict, Any, Tuple
from modules.utils import get_logger

logger = get_logger(__name__)

class ResponseSynthesizer:
    def __init__(self):
        self.logger = get_logger(__name__)

    def synthesize(self, query: str, documents: List[Dict[str, Any]], max_context_length: int = 2000) -> Tuple[str, List[str]]:
        selected_docs = self._select_relevant_documents(documents, query, max_context_length)
        context = self._build_context_string(selected_docs)
        source_citations = [doc.get("metadata", {}).get("source", "unknown") for doc in selected_docs]

        return context, source_citations

    def _select_relevant_documents(self, documents: List[Dict[str, Any]], query: str,
                                   max_length: int) -> List[Dict[str, Any]]:
        selected = []
        current_length = 0

        for doc in documents:
            content = doc.get("metadata", {}).get("content", "")
            content_length = len(content)

            if current_length + content_length <= max_length:
                selected.append(doc)
                current_length += content_length
            elif current_length < max_length:
                trimmed_content = content[:max_length - current_length]
                doc_copy = doc.copy()
                doc_copy["metadata"] = doc.get("metadata", {}).copy()
                doc_copy["metadata"]["content"] = trimmed_content
                selected.append(doc_copy)
                break

        self.logger.info(f"Selected {len(selected)} documents for synthesis")
        return selected

    def _build_context_string(self, documents: List[Dict[str, Any]]) -> str:
        context_parts = []

        for i, doc in enumerate(documents, 1):
            content = doc.get("metadata", {}).get("content", "")
            source = doc.get("metadata", {}).get("source", "unknown")

            context_parts.append(f"[Source {i}: {source}]\n{content}")

        return "\n\n".join(context_parts)

    def merge_sections(self, sections: List[str], separator: str = "\n\n") -> str:
        return separator.join([s for s in sections if s])

    def deduplicate_content(self, documents: List[Dict[str, Any]],
                           similarity_threshold: float = 0.85) -> List[Dict[str, Any]]:
        deduplicated = []

        for doc in documents:
            is_duplicate = False
            doc_content = doc.get("metadata", {}).get("content", "").lower()

            for existing in deduplicated:
                existing_content = existing.get("metadata", {}).get("content", "").lower()
                similarity = self._calculate_similarity(doc_content, existing_content)

                if similarity > similarity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(doc)

        self.logger.info(f"Deduplicated {len(documents)} to {len(deduplicated)} documents")
        return deduplicated

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def balance_sources(self, documents: List[Dict[str, Any]], max_per_source: int = 2) -> List[Dict[str, Any]]:
        source_counts = {}
        balanced = []

        for doc in documents:
            source = doc.get("metadata", {}).get("source", "unknown")

            if source not in source_counts:
                source_counts[source] = 0

            if source_counts[source] < max_per_source:
                balanced.append(doc)
                source_counts[source] += 1

        self.logger.info(f"Balanced documents: {len(documents)} -> {len(balanced)}")
        return balanced

    def organize_by_relevance(self, documents: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        organized = {
            "high_relevance": [],
            "medium_relevance": [],
            "low_relevance": []
        }

        for doc in documents:
            score = doc.get("score", doc.get("context_score", 0.5))

            if score >= 0.7:
                organized["high_relevance"].append(doc)
            elif score >= 0.4:
                organized["medium_relevance"].append(doc)
            else:
                organized["low_relevance"].append(doc)

        return organized
