from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class IterationMetrics:
    iteration_count: int
    total_time: float
    current_confidence: float
    gaps_count: int
    documents_retrieved: int
    query_rewrites: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class IterationController:
    def __init__(self, max_iterations: int = 5, timeout_seconds: int = 60):
        self.logger = get_logger(__name__)
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds

        self.current_iteration = 0
        self.start_time = None
        self.iteration_times: List[float] = []
        self.iteration_history: List[Dict[str, Any]] = []

    def start_iteration(self):
        self.current_iteration += 1
        self.iteration_times.append(0.0)
        start = datetime.now()

        if self.current_iteration == 1:
            self.start_time = start

        self.logger.info(f"Starting iteration {self.current_iteration}")

    def end_iteration(self, metrics: Dict[str, Any] = None):
        if self.current_iteration == 0:
            return

        elapsed = (datetime.now() - (self.start_time or datetime.now())).total_seconds()
        if self.current_iteration <= len(self.iteration_times):
            self.iteration_times[self.current_iteration - 1] = elapsed

        history_entry = {
            "iteration": self.current_iteration,
            "duration": elapsed,
            "metrics": metrics or {}
        }

        self.iteration_history.append(history_entry)
        self.logger.info(f"Completed iteration {self.current_iteration} in {elapsed:.2f}s")

    def should_continue(self, feedback: Dict[str, Any]) -> bool:
        if self.current_iteration >= self.max_iterations:
            self.logger.info(f"Max iterations ({self.max_iterations}) reached")
            return False

        if self._is_timeout():
            self.logger.info("Iteration timeout reached")
            return False

        should_continue = feedback.get("should_continue", False)
        gaps = feedback.get("gaps_identified", [])

        if len(gaps) == 0:
            self.logger.info("No gaps remaining, stopping iteration")
            return False

        return should_continue

    def _is_timeout(self) -> bool:
        if not self.start_time:
            return False

        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > self.timeout_seconds

    def get_elapsed_time(self) -> float:
        if not self.start_time:
            return 0.0

        return (datetime.now() - self.start_time).total_seconds()

    def get_iteration_metrics(self) -> IterationMetrics:
        total_time = self.get_elapsed_time()
        avg_confidence = self._calculate_avg_confidence()
        total_gaps = self._count_total_gaps()
        total_docs = self._count_total_documents()

        return IterationMetrics(
            iteration_count=self.current_iteration,
            total_time=total_time,
            current_confidence=avg_confidence,
            gaps_count=total_gaps,
            documents_retrieved=total_docs,
            query_rewrites=max(0, self.current_iteration - 1)
        )

    def _calculate_avg_confidence(self) -> float:
        if not self.iteration_history:
            return 0.0

        confidences = []
        for entry in self.iteration_history:
            confidence = entry.get("metrics", {}).get("confidence_score", 0)
            if confidence > 0:
                confidences.append(confidence)

        return sum(confidences) / len(confidences) if confidences else 0.0

    def _count_total_gaps(self) -> int:
        total = 0
        for entry in self.iteration_history:
            gaps = entry.get("metrics", {}).get("gaps_identified", [])
            total += len(gaps)

        return total

    def _count_total_documents(self) -> int:
        total = 0
        for entry in self.iteration_history:
            docs = entry.get("metrics", {}).get("documents_retrieved", 0)
            total += docs

        return total

    def get_iteration_history(self) -> List[Dict[str, Any]]:
        return self.iteration_history

    def reset(self):
        self.current_iteration = 0
        self.start_time = None
        self.iteration_times = []
        self.iteration_history = []
        self.logger.info("Iteration controller reset")

    def get_summary(self) -> Dict[str, Any]:
        metrics = self.get_iteration_metrics()

        return {
            "total_iterations": metrics.iteration_count,
            "total_time": metrics.total_time,
            "avg_confidence": metrics.current_confidence,
            "total_gaps": metrics.gaps_count,
            "total_documents": metrics.documents_retrieved,
            "query_rewrites": metrics.query_rewrites,
            "time_per_iteration": sum(self.iteration_times) / len(self.iteration_times) if self.iteration_times else 0,
            "timeout_threshold": self.timeout_seconds,
            "is_timeout": self._is_timeout()
        }
