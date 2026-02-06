from typing import List, Dict, Any, Set
from modules.utils import get_logger

logger = get_logger(__name__)

class QueryExpander:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.synonyms = self._initialize_synonyms()
        self.related_terms = self._initialize_related_terms()

    def _initialize_synonyms(self) -> Dict[str, List[str]]:
        return {
            "python": ["py", "python programming", "python language"],
            "machine learning": ["ml", "deep learning", "neural networks", "ai"],
            "data science": ["data analysis", "data mining", "analytics"],
            "web development": ["web dev", "frontend", "backend", "full stack"],
            "algorithm": ["algorithmic", "computational method", "procedure"],
            "performance": ["efficiency", "speed", "optimization", "latency"],
            "security": ["safety", "protection", "cryptography", "encryption"],
            "database": ["db", "data storage", "persistence", "repository"]
        }

    def _initialize_related_terms(self) -> Dict[str, List[str]]:
        return {
            "python": ["java", "javascript", "c++", "go", "rust"],
            "machine learning": ["statistics", "data mining", "pattern recognition"],
            "data science": ["statistics", "mathematics", "programming"],
            "web development": ["html", "css", "javascript", "frameworks"],
            "database": ["sql", "nosql", "orm", "query language"],
            "algorithm": ["complexity analysis", "sorting", "searching", "optimization"]
        }

    def expand(self, query: str) -> List[str]:
        expanded = [query]

        words = query.lower().split()

        for word in words:
            if word in self.synonyms:
                for synonym in self.synonyms[word]:
                    expanded_query = query.replace(word, synonym)
                    if expanded_query not in expanded:
                        expanded.append(expanded_query)

        for word in words:
            if word in self.related_terms:
                for related in self.related_terms[word]:
                    expanded_query = f"{query} {related}"
                    if expanded_query not in expanded:
                        expanded.append(expanded_query)

        self.logger.info(f"Expanded query from 1 to {len(expanded)} variants")
        return expanded

    def add_synonyms(self, word: str, synonyms: List[str]):
        if word not in self.synonyms:
            self.synonyms[word] = []
        self.synonyms[word].extend(synonyms)
        self.logger.info(f"Added synonyms for '{word}'")

    def add_related_terms(self, word: str, terms: List[str]):
        if word not in self.related_terms:
            self.related_terms[word] = []
        self.related_terms[word].extend(terms)
        self.logger.info(f"Added related terms for '{word}'")

    def get_all_variants(self, query: str, max_variants: int = 5) -> List[str]:
        expanded = self.expand(query)
        return expanded[:max_variants]

    def extract_key_terms(self, query: str) -> Set[str]:
        words = query.lower().split()
        key_terms = set()

        for word in words:
            if len(word) > 3 and word not in ["the", "and", "for", "with"]:
                key_terms.add(word)

        return key_terms
