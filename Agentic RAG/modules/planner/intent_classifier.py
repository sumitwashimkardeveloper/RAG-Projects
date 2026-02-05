from typing import Dict, List, Tuple
from enum import Enum
from modules.utils import get_logger

logger = get_logger(__name__)

class QueryIntent(Enum):
    FACTUAL = "factual"
    REASONING = "reasoning"
    COMPARISON = "comparison"
    DEFINITION = "definition"
    HOW_TO = "how_to"
    OPINION = "opinion"
    SUMMARY = "summary"
    SEARCH = "search"

class IntentClassifier:
    def __init__(self):
        self.intent_keywords = {
            QueryIntent.DEFINITION: [
                "what is", "define", "meaning of", "what does", "explain what"
            ],
            QueryIntent.HOW_TO: [
                "how to", "how do", "how can", "steps to", "process of"
            ],
            QueryIntent.COMPARISON: [
                "compare", "difference between", "vs", "versus", "which is better"
            ],
            QueryIntent.REASONING: [
                "why", "reason for", "cause of", "because", "explanation"
            ],
            QueryIntent.FACTUAL: [
                "when", "where", "who", "which", "how many", "how much"
            ],
            QueryIntent.SUMMARY: [
                "summarize", "summary of", "overview", "brief", "outline"
            ],
            QueryIntent.OPINION: [
                "think about", "opinion on", "best", "worst", "should"
            ]
        }

    def classify(self, query: str) -> Tuple[QueryIntent, float]:
        query_lower = query.lower().strip()
        scores: Dict[QueryIntent, float] = {intent: 0.0 for intent in QueryIntent}

        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    scores[intent] += 1.0

        if not any(scores.values()):
            return QueryIntent.SEARCH, 0.5

        max_intent = max(scores, key=scores.get)
        max_score = scores[max_intent]
        confidence = min(max_score / (len(query_lower.split()) * 0.5), 1.0)

        return max_intent, confidence

    def get_intent_features(self, query: str) -> Dict[str, any]:
        intent, confidence = self.classify(query)

        question_mark = query.strip().endswith("?")
        word_count = len(query.split())
        keyword_count = len([w for w in query.split() if len(w) > 3])

        return {
            "intent": intent.value,
            "confidence": confidence,
            "is_question": question_mark,
            "word_count": word_count,
            "keyword_count": keyword_count
        }
