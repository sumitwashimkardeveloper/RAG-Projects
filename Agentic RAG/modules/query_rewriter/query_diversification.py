from typing import List, Dict, Any
from modules.utils import get_logger, QueryHelper

logger = get_logger(__name__)

class QueryDiversifier:
    def __init__(self):
        self.logger = get_logger(__name__)

    def diversify(self, query: str, num_variants: int = 3) -> List[str]:
        variants = [query]

        keyword_variants = self._create_keyword_variants(query)
        variants.extend(keyword_variants[:num_variants - 1])

        return variants[:num_variants]

    def _create_keyword_variants(self, query: str) -> List[str]:
        keywords = QueryHelper.extract_keywords(query)
        variants = []

        if len(keywords) >= 2:
            for i in range(len(keywords) - 1):
                variant = " ".join(keywords[i:i+2])
                if variant != query:
                    variants.append(variant)

        if len(keywords) >= 3:
            variant = " ".join(keywords[:3])
            if variant != query:
                variants.append(variant)

        return variants

    def create_alternative_phrasings(self, query: str) -> List[str]:
        phrasings = [query]

        phrasings.append(self._convert_to_imperative(query))
        phrasings.append(self._convert_to_interrogative(query))
        phrasings.append(self._convert_to_declarative(query))

        phrasings = [p for p in phrasings if p and p != query]
        return phrasings

    def _convert_to_imperative(self, query: str) -> str:
        if query.endswith("?"):
            base = query[:-1]
        else:
            base = query

        if base.lower().startswith(("what ", "how ", "why ", "when ", "where ")):
            return f"Explain {base}."
        elif base.lower().startswith("is "):
            return f"Show me {base[3:]}."
        else:
            return f"Tell me about {base}."

    def _convert_to_interrogative(self, query: str) -> str:
        if query.endswith("?"):
            return query

        query = query.rstrip(".")

        if query.lower().startswith(("explain ", "show ", "tell me about ")):
            return f"What is {query.split(' ', 1)[1]}?"

        return f"{query}?"

    def _convert_to_declarative(self, query: str) -> str:
        query = query.rstrip("?").rstrip(".")

        if query.lower().startswith(("what is ", "what are ")):
            subject = query.split(" ", 2)[2] if len(query.split(" ", 2)) > 2 else query
            return f"{subject} is a topic of interest."
        elif query.lower().startswith(("how to ", "how do ")):
            return f"The process involves {query.split(' ', 2)[2] if len(query.split(' ', 2)) > 2 else 'it'}."

        return f"{query}."

    def create_aspect_variants(self, query: str) -> List[str]:
        aspects = {
            "overview": f"Overview of {query}",
            "detailed": f"Detailed explanation of {query}",
            "simple": f"Simple explanation of {query}",
            "technical": f"Technical details about {query}",
            "practical": f"Practical aspects of {query}",
            "theoretical": f"Theoretical background of {query}"
        }

        return list(aspects.values())[:3]

    def create_scope_variants(self, query: str) -> List[str]:
        return [
            f"General overview: {query}",
            f"Detailed analysis: {query}",
            f"Quick summary: {query}",
            f"Comprehensive guide: {query}",
            f"Key points about: {query}"
        ]

    def diversify_by_intent(self, query: str) -> List[str]:
        intents = {
            "definition": f"What is {query}?",
            "comparison": f"Compare different aspects of {query}",
            "tutorial": f"How to learn {query}?",
            "benefits": f"What are the benefits of {query}?",
            "limitations": f"What are the limitations of {query}?"
        }

        return list(intents.values())[:3]

    def generate_complementary_queries(self, query: str) -> List[str]:
        complementary = []

        complementary.append(f"{query} tutorial")
        complementary.append(f"{query} examples")
        complementary.append(f"best practices for {query}")
        complementary.append(f"{query} advantages and disadvantages")
        complementary.append(f"common mistakes in {query}")

        return complementary

    def rank_variants(self, variants: List[str], reference_query: str) -> List[str]:
        def similarity_score(v: str) -> float:
            ref_words = set(reference_query.lower().split())
            var_words = set(v.lower().split())

            intersection = len(ref_words & var_words)
            union = len(ref_words | var_words)

            return intersection / union if union > 0 else 0.0

        sorted_variants = sorted(variants, key=lambda v: -similarity_score(v))
        return sorted_variants
