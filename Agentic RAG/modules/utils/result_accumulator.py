from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class AccumulatedResult:
    document_id: str
    content: str
    source: str
    occurrence_count: int = 1
    scores: List[float] = field(default_factory=list)
    iterations_found: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ResultAccumulator:
    def __init__(self, max_documents: int = 50, dedup_threshold: float = 0.9):
        self.logger = get_logger(__name__)
        self.accumulated: Dict[str, AccumulatedResult] = {}
        self.max_documents = max_documents
        self.dedup_threshold = dedup_threshold
        self.current_iteration = 0

    def add_results(self, documents: List[Dict[str, Any]], iteration: int):
        self.current_iteration = iteration

        for doc in documents:
            doc_id = doc.get("id", f"doc_{hash(doc.get('content', ''))}")
            content = doc.get("metadata", {}).get("content", "")
            source = doc.get("metadata", {}).get("source", "unknown")
            score = doc.get("score", 0.5)

            if doc_id in self.accumulated:
                existing = self.accumulated[doc_id]
                existing.occurrence_count += 1
                existing.scores.append(score)
                existing.iterations_found.append(iteration)
                self.logger.debug(f"Updated result {doc_id} (occurrence: {existing.occurrence_count})")
            else:
                result = AccumulatedResult(
                    document_id=doc_id,
                    content=content,
                    source=source,
                    occurrence_count=1,
                    scores=[score],
                    iterations_found=[iteration],
                    metadata=doc.get("metadata", {})
                )
                self.accumulated[doc_id] = result
                self.logger.debug(f"Added new result {doc_id}")

        self.logger.info(f"Accumulated {len(self.accumulated)} total results after iteration {iteration}")

    def get_accumulated_results(self, top_k: int = None) -> List[AccumulatedResult]:
        if top_k is None:
            top_k = self.max_documents

        sorted_results = sorted(
            self.accumulated.values(),
            key=lambda r: (r.occurrence_count, sum(r.scores) / len(r.scores) if r.scores else 0),
            reverse=True
        )

        return sorted_results[:top_k]

    def deduplicate_similar(self) -> int:
        removed = 0
        to_remove = set()

        result_list = list(self.accumulated.values())

        for i in range(len(result_list)):
            if result_list[i].document_id in to_remove:
                continue

            for j in range(i + 1, len(result_list)):
                if result_list[j].document_id in to_remove:
                    continue

                similarity = self._calculate_similarity(
                    result_list[i].content,
                    result_list[j].content
                )

                if similarity > self.dedup_threshold:
                    if result_list[i].occurrence_count >= result_list[j].occurrence_count:
                        to_remove.add(result_list[j].document_id)
                        removed += 1
                    else:
                        to_remove.add(result_list[i].document_id)
                        removed += 1
                        break

        for doc_id in to_remove:
            del self.accumulated[doc_id]

        self.logger.info(f"Removed {removed} duplicate results")
        return removed

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def get_coverage_stats(self) -> Dict[str, Any]:
        if not self.accumulated:
            return {
                "total_unique": 0,
                "total_occurrences": 0,
                "avg_occurrences": 0,
                "sources_count": 0,
                "coverage": 0.0
            }

        total_occurrences = sum(r.occurrence_count for r in self.accumulated.values())
        sources = set(r.source for r in self.accumulated.values())
        avg_occurrences = total_occurrences / len(self.accumulated) if self.accumulated else 0

        coverage = min(len(self.accumulated) / self.max_documents, 1.0)

        return {
            "total_unique": len(self.accumulated),
            "total_occurrences": total_occurrences,
            "avg_occurrences": avg_occurrences,
            "sources_count": len(sources),
            "coverage": coverage
        }

    def get_result_ranking(self) -> List[Tuple[str, float, int]]:
        rankings = []

        for result in self.accumulated.values():
            avg_score = sum(result.scores) / len(result.scores) if result.scores else 0
            combined_score = (avg_score * 0.7) + (result.occurrence_count / self.current_iteration * 0.3) if self.current_iteration > 0 else avg_score
            rankings.append((result.document_id, combined_score, result.occurrence_count))

        return sorted(rankings, key=lambda x: x[1], reverse=True)

    def clear(self):
        self.accumulated = {}
        self.current_iteration = 0
        self.logger.info("Cleared accumulated results")

    def get_iteration_deltas(self) -> Dict[int, int]:
        deltas = {}

        for result in self.accumulated.values():
            for iteration in result.iterations_found:
                deltas[iteration] = deltas.get(iteration, 0) + 1

        return deltas

    def get_summary(self) -> Dict[str, Any]:
        coverage = self.get_coverage_stats()
        ranking = self.get_result_ranking()[:5]

        return {
            "coverage": coverage,
            "top_results": [
                {"id": r[0], "score": r[1], "occurrences": r[2]}
                for r in ranking
            ],
            "current_iteration": self.current_iteration
        }
