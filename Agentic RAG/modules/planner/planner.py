from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from modules.utils import get_logger
from .intent_classifier import IntentClassifier, QueryIntent
from .query_analyzer import QueryAnalyzer
from .search_strategy import SearchStrategySelector, SearchStrategy
from .plan_generator import PlanGenerator, RetrievalPlan

logger = get_logger(__name__)

@dataclass
class QueryPlan:
    original_query: str
    sub_queries: List[str]
    intent: str
    search_strategy: str
    retrieval_plan: Optional[RetrievalPlan] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class QueryPlanner:
    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)

        self.intent_classifier = IntentClassifier()
        self.query_analyzer = QueryAnalyzer()
        self.strategy_selector = SearchStrategySelector(config)
        self.plan_generator = PlanGenerator(config)

    def plan(self, query: str) -> QueryPlan:
        self.logger.info(f"Planning query: {query[:100]}")

        intent, intent_confidence = self.intent_classifier.classify(query)
        analysis = self.query_analyzer.analyze(query)
        strategy = self.strategy_selector.select_strategy(query, analysis)
        retrieval_plan = self.plan_generator.generate_plan(
            query, analysis, strategy.value
        )

        sub_query_texts = [sq.text for sq in analysis.get("sub_queries", [])]

        query_plan = QueryPlan(
            original_query=query,
            sub_queries=sub_query_texts,
            intent=intent.value,
            search_strategy=strategy.value,
            retrieval_plan=retrieval_plan,
            metadata={
                "intent_confidence": intent_confidence,
                "complexity": analysis.get("complexity", 0.0),
                "keywords": analysis.get("keywords", []),
                "entities": analysis.get("entities", []),
                "strategy_explanation": self.strategy_selector.explain_strategy(query, strategy),
                "plan_validation": self.plan_generator.validate_plan(retrieval_plan)
            }
        )

        self.logger.info(f"Query plan created: intent={intent.value}, strategy={strategy.value}")
        return query_plan

    def analyze_query(self, query: str) -> Dict[str, Any]:
        return self.query_analyzer.analyze(query)

    def classify_intent(self, query: str) -> Tuple[str, float]:
        intent, confidence = self.intent_classifier.classify(query)
        return intent.value, confidence

    def select_search_strategy(self, query: str) -> Tuple[str, Dict[str, Any]]:
        strategy = self.strategy_selector.select_strategy(query)
        params = self.strategy_selector.get_retrieval_params(strategy)
        return strategy.value, params

    def get_intent_features(self, query: str) -> Dict[str, Any]:
        return self.intent_classifier.get_intent_features(query)

    def get_plan_steps(self, query_plan: QueryPlan) -> List[Dict[str, Any]]:
        if not query_plan.retrieval_plan:
            return []

        return [
            {
                "step": step.step_number,
                "action": step.action,
                "description": step.description,
                "dependencies": step.dependencies,
                "cost": step.estimated_cost
            }
            for step in query_plan.retrieval_plan.steps
        ]

    def explain_plan(self, query_plan: QueryPlan) -> str:
        lines = []
        lines.append(f"Query: {query_plan.original_query}")
        lines.append(f"Intent: {query_plan.intent}")
        lines.append(f"Strategy: {query_plan.search_strategy}")

        if query_plan.sub_queries:
            lines.append(f"Sub-queries: {len(query_plan.sub_queries)}")
            for i, sq in enumerate(query_plan.sub_queries, 1):
                lines.append(f"  {i}. {sq}")

        if query_plan.retrieval_plan:
            lines.append(f"Retrieval Plan ({len(query_plan.retrieval_plan.steps)} steps):")
            for step in query_plan.retrieval_plan.steps:
                lines.append(f"  Step {step.step_number}: {step.action}")

        return "\n".join(lines)
