import time
import statistics
from typing import List, Dict, Any
from pipeline import AgenticRAGPipeline
from modules.utils import get_logger, get_config, QueryMetrics
from modules.utils.monitoring import MetricsCollector

logger = get_logger(__name__)

class PerformanceTester:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.pipeline = AgenticRAGPipeline(self.config)
        self.metrics_collector = MetricsCollector()

    def test_query_latency(self, queries: List[str]) -> Dict[str, Any]:
        self.logger.info(f"Testing latency for {len(queries)} queries")

        latencies = []

        for query in queries:
            start_time = time.time()
            result = self.pipeline.process(query)
            latency = time.time() - start_time
            latencies.append(latency)

            metric = QueryMetrics(
                query=query,
                response_time=latency,
                iterations=result.get("iterations", {}).get("total_iterations", 0),
                confidence_score=result.get("iterations", {}).get("avg_confidence", 0.0),
                success=result.get("success", False)
            )
            self.metrics_collector.record_query(metric)

            self.logger.info(f"Query latency: {latency:.2f}s")

        return {
            "total_queries": len(queries),
            "avg_latency": statistics.mean(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "median_latency": statistics.median(latencies),
            "std_dev": statistics.stdev(latencies) if len(latencies) > 1 else 0,
            "queries_per_second": len(queries) / sum(latencies) if sum(latencies) > 0 else 0
        }

    def test_memory_usage(self) -> Dict[str, Any]:
        self.logger.info("Testing memory usage")

        import psutil
        process = psutil.Process()

        initial_memory = process.memory_info().rss / 1024 / 1024

        test_queries = [
            "What is Python?",
            "Machine learning basics",
            "AI explained"
        ]

        for query in test_queries:
            self.pipeline.process(query)

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_used = final_memory - initial_memory

        return {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_used_mb": memory_used,
            "peak_memory_mb": process.memory_info().rss / 1024 / 1024
        }

    def test_throughput(self, num_queries: int = 10) -> Dict[str, Any]:
        self.logger.info(f"Testing throughput with {num_queries} queries")

        queries = [f"Test query {i}" for i in range(num_queries)]

        start_time = time.time()
        results = []

        for query in queries:
            try:
                result = self.pipeline.process(query)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error processing query: {e}")

        total_time = time.time() - start_time
        successful = sum(1 for r in results if r.get("success"))

        return {
            "total_queries": num_queries,
            "successful_queries": successful,
            "failed_queries": num_queries - successful,
            "total_time_seconds": total_time,
            "throughput_qps": num_queries / total_time if total_time > 0 else 0,
            "success_rate": (successful / num_queries * 100) if num_queries > 0 else 0
        }

    def test_accuracy_against_benchmarks(self, benchmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
        self.logger.info(f"Testing accuracy against {len(benchmarks)} benchmarks")

        results = []

        for benchmark in benchmarks:
            query = benchmark["query"]
            expected_topics = benchmark.get("expected_topics", [])
            min_confidence = benchmark.get("min_confidence", 0.5)

            result = self.pipeline.process(query)

            if result.get("success"):
                answer = result.get("answer", "").lower()
                topics_found = sum(1 for topic in expected_topics if topic.lower() in answer)
                confidence = result.get("iterations", {}).get("avg_confidence", 0.0)

                results.append({
                    "query": query,
                    "topics_found": topics_found,
                    "expected_topics": len(expected_topics),
                    "coverage": (topics_found / len(expected_topics) * 100) if expected_topics else 0,
                    "confidence": confidence,
                    "meets_confidence_threshold": confidence >= min_confidence
                })

        avg_coverage = statistics.mean([r["coverage"] for r in results]) if results else 0
        avg_confidence = statistics.mean([r["confidence"] for r in results]) if results else 0

        return {
            "total_benchmarks": len(benchmarks),
            "avg_topic_coverage": avg_coverage,
            "avg_confidence": avg_confidence,
            "results": results
        }

    def generate_performance_report(self) -> Dict[str, Any]:
        self.logger.info("Generating performance report")

        test_queries = [
            "What is Python?",
            "Machine learning",
            "Deep learning",
            "Neural networks",
            "AI basics"
        ]

        latency_results = self.test_query_latency(test_queries)

        metrics_summary = self.metrics_collector.get_summary()
        performance_report = self.metrics_collector.get_performance_report()

        throughput = self.test_throughput(5)

        return {
            "latency": latency_results,
            "throughput": throughput,
            "metrics_summary": metrics_summary,
            "performance_report": performance_report,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }

if __name__ == "__main__":
    tester = PerformanceTester()

    report = tester.generate_performance_report()

    import json
    print(json.dumps(report, indent=2))
