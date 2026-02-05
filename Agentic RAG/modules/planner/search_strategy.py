from typing import List, Dict, Any
from enum import Enum
from modules.utils import get_logger

logger = get_logger(__name__)

class SearchStrategy(Enum):
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    DENSE_PASSAGE = "dense_passage"

class SearchStrategySelector:
    def __init__(self, config=None):
        self.config = config
        self.strategy_rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[str, Any]:
        return {
            "semantic": {
                "weight": 0.7,
                "triggers": ["meaning", "concept", "understanding", "definition"],
                "best_for": ["reasoning", "semantic_search", "complex_questions"]
            },
            "keyword": {
                "weight": 0.3,
                "triggers": ["specific", "exact", "named", "entities"],
                "best_for": ["factual_questions", "named_entities", "simple_queries"]
            },
            "hybrid": {
                "weight": 0.5,
                "triggers": ["combined", "comprehensive", "multiple"],
                "best_for": ["complex_queries", "multi_faceted", "general_search"]
            },
            "dense_passage": {
                "weight": 0.8,
                "triggers": ["passage", "document", "article"],
                "best_for": ["passage_retrieval", "long_form", "detailed_answers"]
            }
        }

    def select_strategy(self, query: str, query_features: Dict[str, Any] = None) -> SearchStrategy:
        query_lower = query.lower()

        if self._is_keyword_heavy_query(query):
            return SearchStrategy.KEYWORD

        if self._is_complex_query(query):
            return SearchStrategy.HYBRID

        if self._is_dense_passage_query(query):
            return SearchStrategy.DENSE_PASSAGE

        return SearchStrategy.SEMANTIC

    def _is_keyword_heavy_query(self, query: str) -> bool:
        query_lower = query.lower()
        keyword_triggers = ["who is", "where is", "when was", "what is the name"]

        entity_indicators = sum(1 for word in query.split() if word[0].isupper())

        has_trigger = any(trigger in query_lower for trigger in keyword_triggers)
        has_entities = entity_indicators > 1

        return has_trigger or has_entities

    def _is_complex_query(self, query: str) -> bool:
        complexity_indicators = [
            query.count(",") >= 1,
            " and " in query.lower() or " or " in query.lower(),
            len(query.split()) > 15,
            query.count("(") > 0 or query.count(")") > 0
        ]

        return sum(complexity_indicators) >= 2

    def _is_dense_passage_query(self, query: str) -> bool:
        passage_keywords = ["summarize", "explain", "describe", "overview", "article", "passage"]
        return any(kw in query.lower() for kw in passage_keywords)

    def get_retrieval_params(self, strategy: SearchStrategy) -> Dict[str, Any]:
        params = {
            "strategy": strategy.value,
            "top_k": 5,
            "score_threshold": 0.5
        }

        if strategy == SearchStrategy.SEMANTIC:
            params.update({
                "top_k": 5,
                "score_threshold": 0.6,
                "use_embeddings": True
            })
        elif strategy == SearchStrategy.KEYWORD:
            params.update({
                "top_k": 10,
                "score_threshold": 0.4,
                "use_bm25": True
            })
        elif strategy == SearchStrategy.HYBRID:
            params.update({
                "top_k": 8,
                "score_threshold": 0.5,
                "use_embeddings": True,
                "use_bm25": True,
                "semantic_weight": 0.7,
                "keyword_weight": 0.3
            })
        elif strategy == SearchStrategy.DENSE_PASSAGE:
            params.update({
                "top_k": 3,
                "score_threshold": 0.65,
                "passage_length": 1000
            })

        return params

    def explain_strategy(self, query: str, strategy: SearchStrategy) -> str:
        explanations = {
            SearchStrategy.SEMANTIC: "Using semantic search for conceptual understanding",
            SearchStrategy.KEYWORD: "Using keyword search for specific entity matching",
            SearchStrategy.HYBRID: "Using hybrid approach combining semantic and keyword search",
            SearchStrategy.DENSE_PASSAGE: "Using dense passage retrieval for comprehensive passages"
        }

        return explanations.get(strategy, "Using default search strategy")
