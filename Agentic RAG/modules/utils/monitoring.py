from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from pathlib import Path
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class QueryMetrics:
    query: str
    response_time: float
    iterations: int
    confidence_score: float
    success: bool
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

class MetricsCollector:
    def __init__(self, metrics_file: str = "logs/metrics.json"):
        self.logger = get_logger(__name__)
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.query_metrics: List[QueryMetrics] = []
        self._load_metrics()

    def _load_metrics(self):
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.query_metrics = [QueryMetrics(**m) for m in data[:1000]]
        except Exception as e:
            self.logger.warning(f"Error loading metrics: {e}")

    def record_query(self, metric: QueryMetrics):
        metric.timestamp = datetime.now().isoformat()
        self.query_metrics.append(metric)

        if len(self.query_metrics) % 100 == 0:
            self._save_metrics()

    def _save_metrics(self):
        try:
            with open(self.metrics_file, 'w') as f:
                data = [
                    {
                        "query": m.query[:100],
                        "response_time": m.response_time,
                        "iterations": m.iterations,
                        "confidence_score": m.confidence_score,
                        "success": m.success,
                        "timestamp": m.timestamp,
                        "metadata": m.metadata
                    }
                    for m in self.query_metrics[-1000:]
                ]
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")

    def get_summary(self, hours: int = 24) -> Dict[str, Any]:
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_metrics = [
            m for m in self.query_metrics
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

        if not recent_metrics:
            return self._empty_summary()

        total_queries = len(recent_metrics)
        successful = sum(1 for m in recent_metrics if m.success)
        avg_response_time = sum(m.response_time for m in recent_metrics) / total_queries
        avg_confidence = sum(m.confidence_score for m in recent_metrics) / total_queries
        avg_iterations = sum(m.iterations for m in recent_metrics) / total_queries

        return {
            "total_queries": total_queries,
            "successful_queries": successful,
            "success_rate": (successful / total_queries * 100) if total_queries > 0 else 0,
            "avg_response_time": avg_response_time,
            "avg_confidence": avg_confidence,
            "avg_iterations": avg_iterations,
            "min_response_time": min(m.response_time for m in recent_metrics),
            "max_response_time": max(m.response_time for m in recent_metrics)
        }

    def _empty_summary(self) -> Dict[str, Any]:
        return {
            "total_queries": 0,
            "successful_queries": 0,
            "success_rate": 0,
            "avg_response_time": 0,
            "avg_confidence": 0,
            "avg_iterations": 0,
            "min_response_time": 0,
            "max_response_time": 0
        }

    def get_performance_report(self) -> Dict[str, Any]:
        if not self.query_metrics:
            return {"status": "no_data"}

        response_times = [m.response_time for m in self.query_metrics[-100:]]
        confidence_scores = [m.confidence_score for m in self.query_metrics[-100:]]

        percentiles = {
            "p50": sorted(response_times)[len(response_times)//2] if response_times else 0,
            "p95": sorted(response_times)[int(len(response_times)*0.95)] if response_times else 0,
            "p99": sorted(response_times)[int(len(response_times)*0.99)] if response_times else 0
        }

        return {
            "total_queries_processed": len(self.query_metrics),
            "response_time_percentiles": percentiles,
            "avg_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "confidence_std_dev": self._calculate_std_dev(confidence_scores)
        }

    def _calculate_std_dev(self, values: List[float]) -> float:
        if not values:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def clear(self):
        self.query_metrics = []
        self.logger.info("Cleared metrics")
