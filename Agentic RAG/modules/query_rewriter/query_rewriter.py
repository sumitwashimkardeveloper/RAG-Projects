from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from modules.utils import get_logger
from .query_expansion import QueryExpander
from .query_reformulation import QueryReformulator
from .query_diversification import QueryDiversifier
from .query_learning import QueryLearningEngine, LearnedReformulation

logger = get_logger(__name__)

@dataclass
class RewrittenQuery:
    original_query: str
    rewritten_query: str
    strategy: str
    confidence_score: float = 0.0
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class QueryRewriter:
    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)

        self.expander = QueryExpander()
        self.reformulator = QueryReformulator()
        self.diversifier = QueryDiversifier()
        self.learning_engine = QueryLearningEngine()

    def rewrite(self, query: str, feedback: Dict[str, Any] = None) -> RewrittenQuery:
        self.logger.info(f"Rewriting query: {query[:100]}")

        gaps = feedback.get("gaps_identified", []) if feedback else []
        confidence = feedback.get("confidence_score", 0.0) if feedback else 0.0

        strategy = self._select_rewrite_strategy(query, gaps, confidence)

        if strategy == "learned":
            rewritten, alt_queries = self._apply_learned_reformulations(query)
        elif strategy == "gap_based":
            rewritten_list = self.reformulate_query(query, gaps)
            rewritten = rewritten_list[0] if rewritten_list else query
            alt_queries = rewritten_list[1:] if len(rewritten_list) > 1 else []
        elif strategy == "expansion":
            expanded = self.expand_query(query)
            rewritten = expanded[0] if expanded else query
            alt_queries = expanded[1:]
        else:
            diversified = self.diversify_query(query)
            rewritten = diversified[0] if diversified else query
            alt_queries = diversified[1:]

        confidence_score = self._calculate_rewrite_confidence(strategy, confidence)

        rewritten_query = RewrittenQuery(
            original_query=query,
            rewritten_query=rewritten,
            strategy=strategy,
            confidence_score=confidence_score,
            alternatives=alt_queries[:3],
            metadata={
                "gaps_addressed": len(gaps),
                "strategy_applied": strategy,
                "original_confidence": confidence
            }
        )

        self.logger.info(f"Rewrote query using {strategy} strategy")
        return rewritten_query

    def expand_query(self, query: str) -> List[str]:
        return self.expander.expand(query)

    def reformulate_query(self, query: str, gaps: List[str] = None) -> List[str]:
        if gaps:
            return self.reformulator.reformulate_based_on_gaps(query, gaps)
        return self.reformulator.reformulate(query)

    def diversify_query(self, query: str) -> List[str]:
        return self.diversifier.diversify(query, num_variants=3)

    def apply_learned_reformulations(self, query: str) -> List[str]:
        return self.learning_engine.get_learned_reformulations(query)

    def _apply_learned_reformulations(self, query: str) -> Tuple[str, List[str]]:
        learned = self.learning_engine.get_learned_reformulations(query)
        if learned:
            return learned[0], learned[1:]
        return query, []

    def _select_rewrite_strategy(self, query: str, gaps: List[str], confidence: float) -> str:
        best_reformulation, score = self.learning_engine.get_best_reformulation(query)
        if score >= 0.7:
            return "learned"

        if gaps and len(gaps) > 0:
            return "gap_based"

        if confidence < 0.5:
            return "expansion"

        return "diversification"

    def _calculate_rewrite_confidence(self, strategy: str, original_confidence: float) -> float:
        strategy_boost = {
            "learned": 0.25,
            "gap_based": 0.20,
            "expansion": 0.15,
            "diversification": 0.10
        }

        boost = strategy_boost.get(strategy, 0.0)
        new_confidence = min(original_confidence + boost, 1.0)

        return new_confidence

    def record_rewrite_success(self, original: str, rewritten: str, success_score: float,
                              gap_type: str = "", metadata: Dict[str, Any] = None):
        self.learning_engine.record_reformulation(original, rewritten, success_score, gap_type, metadata)
        self.logger.info(f"Recorded rewrite success: {success_score:.2f}")

    def get_rewrite_statistics(self) -> Dict[str, Any]:
        return self.learning_engine.get_statistics()

    def get_alternative_queries(self, query: str) -> List[str]:
        alternatives = []

        alternatives.extend(self.expand_query(query)[:2])
        alternatives.extend(self.diversify_query(query)[:2])
        alternatives.extend(self.apply_learned_reformulations(query)[:1])

        return list(set(alternatives))[:5]

    def create_query_variations(self, query: str) -> Dict[str, List[str]]:
        return {
            "expanded": self.expand_query(query)[:3],
            "reformulated": self.reformulate_query(query)[:3],
            "diversified": self.diversify_query(query)[:3],
            "learned": self.apply_learned_reformulations(query)[:3]
        }

    def get_learning_insights(self) -> Dict[str, Any]:
        stats = self.learning_engine.get_statistics()
        top = self.learning_engine.get_top_reformulations(5)

        return {
            "statistics": stats,
            "top_reformulations": [
                {"original": t[0], "reformulated": t[1], "score": t[2]}
                for t in top
            ]
        }
