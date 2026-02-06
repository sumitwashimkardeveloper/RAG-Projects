from typing import List, Dict, Any
from modules.utils import get_logger, QueryHelper

logger = get_logger(__name__)

class QueryReformulator:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.reformulation_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[str, List[str]]:
        return {
            "temporal": [
                "What is the timeline of {subject}?",
                "When did {subject} occur?",
                "Historical progression of {subject}",
                "{subject} through time"
            ],
            "spatial": [
                "Where is {subject} located?",
                "Geographic distribution of {subject}",
                "{subject} in different regions",
                "Geographical aspects of {subject}"
            ],
            "causal": [
                "Why does {subject} occur?",
                "Causes of {subject}",
                "What leads to {subject}?",
                "Factors influencing {subject}"
            ],
            "procedural": [
                "How to {subject}?",
                "Steps for {subject}",
                "Process of {subject}",
                "Method for {subject}"
            ],
            "comparative": [
                "Compare {subject} with alternatives",
                "Differences in {subject}",
                "{subject} vs other approaches",
                "Advantages and disadvantages of {subject}"
            ],
            "definition": [
                "Define {subject}",
                "What is {subject}?",
                "Meaning of {subject}",
                "Explanation of {subject}"
            ]
        }

    def reformulate(self, query: str, gap_type: str = None) -> List[str]:
        reformulated = [query]

        if gap_type and gap_type in self.reformulation_patterns:
            patterns = self.reformulation_patterns[gap_type]
            subject = self._extract_subject(query)

            for pattern in patterns:
                try:
                    reformulated_query = pattern.format(subject=subject)
                    if reformulated_query != query and reformulated_query not in reformulated:
                        reformulated.append(reformulated_query)
                except KeyError:
                    continue

        structural_variants = self._create_structural_variants(query)
        reformulated.extend(structural_variants)

        self.logger.info(f"Generated {len(reformulated)} reformulations")
        return reformulated[:5]

    def _extract_subject(self, query: str) -> str:
        question_words = ["what", "when", "where", "why", "how", "is", "are", "do", "does"]
        words = query.lower().split()

        for i, word in enumerate(words):
            if word not in question_words and len(word) > 2:
                return query[query.lower().index(word):]

        return query

    def _create_structural_variants(self, query: str) -> List[str]:
        variants = []

        if query.endswith("?"):
            statement = query[:-1] + "."
            variants.append(statement)

        if "and" in query.lower():
            parts = query.split(" and ")
            for part in parts:
                if part.strip() != query:
                    variants.append(part.strip())

        if not query.endswith("?") and not query.endswith("."):
            variants.append(query + "?")

        keywords = QueryHelper.extract_keywords(query)
        if len(keywords) > 2:
            keyword_query = " ".join(keywords[:3])
            variants.append(keyword_query)

        return [v for v in variants if v != query]

    def reformulate_based_on_gaps(self, query: str, gaps: List[str]) -> List[str]:
        reformulated = [query]

        gap_types = set()
        for gap in gaps:
            if "temporal" in gap.lower() or "when" in gap.lower():
                gap_types.add("temporal")
            elif "spatial" in gap.lower() or "location" in gap.lower():
                gap_types.add("spatial")
            elif "causal" in gap.lower() or "why" in gap.lower():
                gap_types.add("causal")
            elif "procedural" in gap.lower() or "how" in gap.lower():
                gap_types.add("procedural")

        for gap_type in gap_types:
            reformulated.extend(self.reformulate(query, gap_type))

        return list(set(reformulated))[:5]

    def add_pattern(self, gap_type: str, pattern: str):
        if gap_type not in self.reformulation_patterns:
            self.reformulation_patterns[gap_type] = []
        self.reformulation_patterns[gap_type].append(pattern)
        self.logger.info(f"Added pattern for '{gap_type}'")

    def get_reformulation_explanation(self, original: str, reformulated: str) -> str:
        if original == reformulated:
            return "No reformulation needed"

        if len(reformulated) > len(original):
            return "Expanded query with additional context"
        elif len(reformulated) < len(original):
            return "Simplified query to key concepts"
        else:
            return "Restructured query for better matching"
