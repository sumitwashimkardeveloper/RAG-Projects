from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from modules.utils import get_logger
from .relevance_evaluator import RelevanceEvaluator
from .confidence_scorer import ConfidenceScorer
from .gap_detector import GapDetector
from .completeness_checker import CompletenessChecker

logger = get_logger(__name__)

@dataclass
class CriticFeedback:
    is_relevant: bool
    confidence_score: float
    gaps_identified: List[str] = field(default_factory=list)
    completeness_score: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    should_continue: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

class Critic:
    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)

        self.relevance_evaluator = RelevanceEvaluator()
        self.confidence_scorer = ConfidenceScorer()
        self.gap_detector = GapDetector()
        self.completeness_checker = CompletenessChecker()

        self.confidence_threshold = self.config.get("critic.confidence_threshold", 0.6) if config else 0.6
        self.max_iterations = self.config.get("critic.max_feedback_iterations", 3) if config else 3

    def evaluate(self, query: str, documents: List[Dict[str, Any]], context: Dict[str, Any] = None) -> CriticFeedback:
        self.logger.info(f"Evaluating {len(documents)} documents")

        is_relevant, relevance_score = self.evaluate_relevance(query, documents)
        confidence_score = self.calculate_confidence(documents, query)
        gaps = self.detect_gaps(query, documents)
        is_complete, completeness_score = self.check_completeness(query, documents)

        should_continue = (
            not is_complete or
            len(gaps) > 0 and confidence_score < self.confidence_threshold
        )

        suggestions = self._generate_suggestions(
            is_relevant, confidence_score, gaps, is_complete
        )

        feedback = CriticFeedback(
            is_relevant=is_relevant,
            confidence_score=confidence_score,
            gaps_identified=gaps,
            completeness_score=completeness_score,
            suggestions=suggestions,
            should_continue=should_continue,
            metadata={
                "relevance_score": relevance_score,
                "document_count": len(documents),
                "evaluation_timestamp": self._get_timestamp()
            }
        )

        self.logger.info(f"Evaluation complete: relevant={is_relevant}, confidence={confidence_score:.2f}")
        return feedback

    def evaluate_relevance(self, query: str, documents: List[Dict[str, Any]]) -> Tuple[bool, float]:
        if not documents:
            return False, 0.0

        relevant_docs = self.relevance_evaluator.filter_by_relevance(query, documents)
        is_relevant = len(relevant_docs) > 0
        avg_relevance = (
            sum(doc.get("relevance_score", 0) for doc in relevant_docs) / len(relevant_docs)
            if relevant_docs else 0.0
        )

        return is_relevant, avg_relevance

    def calculate_confidence(self, documents: List[Dict[str, Any]], query: str = "") -> float:
        return self.confidence_scorer.score(documents, query)

    def detect_gaps(self, query: str, documents: List[Dict[str, Any]]) -> List[str]:
        return self.gap_detector.detect(query, documents)

    def check_completeness(self, query: str, documents: List[Dict[str, Any]]) -> Tuple[bool, float]:
        return self.completeness_checker.check(query, documents)

    def get_detailed_report(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        feedback = self.evaluate(query, documents)

        relevance_details = {
            "most_relevant": self.relevance_evaluator.find_most_relevant(query, documents),
            "batch_scores": self.relevance_evaluator.evaluate_batch(query, documents)
        }

        confidence_details = self.confidence_scorer.score_distribution(documents)

        gap_details = self.gap_detector.quantify_gaps(query, documents)

        completeness_details = self.completeness_checker.get_completeness_report(query, documents)

        return {
            "feedback": feedback,
            "relevance_details": relevance_details,
            "confidence_details": confidence_details,
            "gap_details": gap_details,
            "completeness_details": completeness_details
        }

    def _generate_suggestions(self, is_relevant: bool, confidence: float,
                             gaps: List[str], is_complete: bool) -> List[str]:
        suggestions = []

        if not is_relevant:
            suggestions.append("Retrieved documents are not relevant. Reformulate the query.")

        if confidence < self.confidence_threshold:
            suggestions.append(f"Confidence is low ({confidence:.2f}). Need more relevant documents.")

        if gaps:
            suggestions.append(f"Detected {len(gaps)} information gaps. Consider expanding the search.")

        if not is_complete:
            suggestions.append("Documents don't comprehensively answer the query.")

        if len(suggestions) == 0:
            suggestions.append("Evaluation passed. Ready to generate answer.")

        return suggestions

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()

    def should_continue_iteration(self, feedback: CriticFeedback, iteration: int) -> bool:
        if iteration >= self.max_iterations:
            return False

        return feedback.should_continue

    def get_critique_summary(self, feedback: CriticFeedback) -> str:
        lines = []
        lines.append("=== Critic Evaluation Summary ===")
        lines.append(f"Relevance: {'✓' if feedback.is_relevant else '✗'}")
        lines.append(f"Confidence: {feedback.confidence_score:.2f}")
        lines.append(f"Completeness: {feedback.completeness_score:.2f}")

        if feedback.gaps_identified:
            lines.append(f"Gaps ({len(feedback.gaps_identified)}):")
            for gap in feedback.gaps_identified[:3]:
                lines.append(f"  - {gap}")

        if feedback.suggestions:
            lines.append("Suggestions:")
            for suggestion in feedback.suggestions[:3]:
                lines.append(f"  - {suggestion}")

        return "\n".join(lines)
