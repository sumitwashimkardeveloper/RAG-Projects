from typing import List, Dict, Any
from dataclasses import dataclass
from modules.utils import get_logger, QueryHelper

logger = get_logger(__name__)

@dataclass
class SubQuery:
    text: str
    priority: int
    focus_area: str
    metadata: Dict[str, Any] = None

class QueryAnalyzer:
    def __init__(self):
        self.conjunctions = ["and", "or", "but", "also"]
        self.question_words = ["what", "how", "why", "when", "where", "who", "which"]

    def analyze(self, query: str) -> Dict[str, Any]:
        normalized = QueryHelper.normalize_query(query)
        keywords = QueryHelper.extract_keywords(query)

        entities = self._extract_entities(query)
        sub_queries = self._decompose_query(query)
        complexity_score = self._calculate_complexity(query)

        return {
            "original_query": query,
            "normalized_query": normalized,
            "keywords": keywords,
            "entities": entities,
            "sub_queries": sub_queries,
            "complexity": complexity_score,
            "has_multiple_parts": len(sub_queries) > 1
        }

    def _extract_entities(self, query: str) -> List[str]:
        entities = []
        words = query.split()

        for i, word in enumerate(words):
            if word[0].isupper() and word not in ["The", "This", "That", "A", "An"]:
                entities.append(word)

            if i > 0 and words[i-1][0].isupper() and word[0].isupper():
                if entities and words[i-1] in entities:
                    idx = entities.index(words[i-1])
                    entities[idx] = words[i-1] + " " + word
                    if word in entities:
                        entities.remove(word)

        return entities

    def _decompose_query(self, query: str) -> List[SubQuery]:
        sub_queries = []
        normalized = QueryHelper.normalize_query(query)

        for conj in self.conjunctions:
            if conj in normalized:
                parts = normalized.split(conj)
                for priority, part in enumerate(parts):
                    part = part.strip()
                    if part:
                        focus_area = self._identify_focus_area(part)
                        sub_queries.append(SubQuery(
                            text=part,
                            priority=priority,
                            focus_area=focus_area
                        ))
                if sub_queries:
                    return sub_queries

        focus_area = self._identify_focus_area(normalized)
        sub_queries.append(SubQuery(
            text=normalized,
            priority=0,
            focus_area=focus_area
        ))

        return sub_queries

    def _identify_focus_area(self, query_part: str) -> str:
        focus_areas = {
            "definition": ["what", "meaning", "define"],
            "process": ["how", "steps", "process"],
            "reason": ["why", "reason", "cause"],
            "comparison": ["compare", "difference", "versus"],
            "facts": ["when", "where", "who", "which", "statistics"]
        }

        query_lower = query_part.lower()
        for area, keywords in focus_areas.items():
            if any(kw in query_lower for kw in keywords):
                return area

        return "general"

    def _calculate_complexity(self, query: str) -> float:
        word_count = len(query.split())
        clause_count = query.count(",") + query.count(";")
        conjunctions_count = sum(1 for conj in self.conjunctions if conj in query.lower())

        complexity = (word_count * 0.1) + (clause_count * 0.3) + (conjunctions_count * 0.2)
        return min(complexity, 1.0)
