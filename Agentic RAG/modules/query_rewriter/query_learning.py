from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class LearnedReformulation:
    original_query: str
    reformulated_query: str
    success_score: float
    gap_type: str = ""
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class QueryLearningEngine:
    def __init__(self, cache_file: str = "cache/reformulations.json"):
        self.logger = get_logger(__name__)
        self.cache_file = Path(cache_file)
        self.learned_reformulations: Dict[str, List[LearnedReformulation]] = {}
        self.success_threshold = 0.7

        self._load_cache()

    def _load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    for original, reformulations in data.items():
                        self.learned_reformulations[original] = [
                            LearnedReformulation(**r) for r in reformulations
                        ]
                self.logger.info(f"Loaded {len(self.learned_reformulations)} learned reformulations")
            except Exception as e:
                self.logger.warning(f"Error loading cache: {e}")

    def _save_cache(self):
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            data = {}
            for original, reformulations in self.learned_reformulations.items():
                data[original] = [
                    {
                        "original_query": r.original_query,
                        "reformulated_query": r.reformulated_query,
                        "success_score": r.success_score,
                        "gap_type": r.gap_type,
                        "timestamp": r.timestamp,
                        "metadata": r.metadata
                    }
                    for r in reformulations
                ]

            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")

    def record_reformulation(self, original: str, reformulated: str, success_score: float,
                            gap_type: str = "", metadata: Dict[str, Any] = None):
        if success_score < 0.0 or success_score > 1.0:
            return

        learned = LearnedReformulation(
            original_query=original,
            reformulated_query=reformulated,
            success_score=success_score,
            gap_type=gap_type,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        if original not in self.learned_reformulations:
            self.learned_reformulations[original] = []

        self.learned_reformulations[original].append(learned)

        if success_score >= self.success_threshold:
            self.logger.info(f"Recorded successful reformulation: {original} -> {reformulated}")

        self._save_cache()

    def get_learned_reformulations(self, query: str, gap_type: str = None) -> List[str]:
        if query not in self.learned_reformulations:
            return []

        reformulations = self.learned_reformulations[query]

        if gap_type:
            reformulations = [r for r in reformulations if r.gap_type == gap_type]

        successful = [r for r in reformulations if r.success_score >= self.success_threshold]

        if not successful:
            successful = sorted(reformulations, key=lambda x: x.success_score, reverse=True)[:3]

        return [r.reformulated_query for r in successful]

    def get_best_reformulation(self, query: str) -> Tuple[str, float]:
        if query not in self.learned_reformulations:
            return query, 0.0

        reformulations = self.learned_reformulations[query]
        best = max(reformulations, key=lambda x: x.success_score)

        return best.reformulated_query, best.success_score

    def get_statistics(self) -> Dict[str, Any]:
        total_reformulations = sum(len(r) for r in self.learned_reformulations.values())
        successful = sum(
            len([r for r in reformulations if r.success_score >= self.success_threshold])
            for reformulations in self.learned_reformulations.values()
        )

        if total_reformulations == 0:
            success_rate = 0.0
        else:
            success_rate = successful / total_reformulations

        return {
            "total_queries_with_reformulations": len(self.learned_reformulations),
            "total_reformulations": total_reformulations,
            "successful_reformulations": successful,
            "success_rate": success_rate
        }

    def clear_cache(self):
        self.learned_reformulations = {}
        if self.cache_file.exists():
            self.cache_file.unlink()
        self.logger.info("Cleared reformulation cache")

    def get_top_reformulations(self, limit: int = 10) -> List[Tuple[str, str, float]]:
        all_reformulations = []

        for original, reformulations in self.learned_reformulations.items():
            for r in reformulations:
                if r.success_score >= self.success_threshold:
                    all_reformulations.append((original, r.reformulated_query, r.success_score))

        sorted_reformulations = sorted(all_reformulations, key=lambda x: x[2], reverse=True)
        return sorted_reformulations[:limit]

    def update_success_score(self, original: str, reformulated: str, new_score: float):
        if original not in self.learned_reformulations:
            return

        for r in self.learned_reformulations[original]:
            if r.reformulated_query == reformulated:
                r.success_score = new_score
                self._save_cache()
                self.logger.info(f"Updated success score for reformulation: {reformulated}")
                return
