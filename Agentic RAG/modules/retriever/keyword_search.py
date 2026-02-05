from typing import List, Dict, Any, Optional, Set
from collections import Counter
from modules.utils import get_logger, QueryHelper

logger = get_logger(__name__)

class BM25:
    def __init__(self, documents: List[Dict[str, Any]] = None, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.avgdl = 0
        self.idf = {}
        self.doc_vectors = {}
        self.documents = documents or []

        if documents:
            self._build_index(documents)

    def _build_index(self, documents: List[Dict[str, Any]]):
        doc_texts = []
        self.documents = documents

        for doc in documents:
            content = doc.get("content", "")
            tokens = self._tokenize(content)
            doc_texts.append(tokens)

        if doc_texts:
            self.avgdl = sum(len(doc) for doc in doc_texts) / len(doc_texts)

        num_docs = len(doc_texts)
        all_tokens = set()

        for tokens in doc_texts:
            all_tokens.update(tokens)

        for token in all_tokens:
            doc_count = sum(1 for tokens in doc_texts if token in tokens)
            self.idf[token] = (num_docs - doc_count + 0.5) / (doc_count + 0.5)

        self.doc_vectors = [Counter(tokens) for tokens in doc_texts]

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        tokens = text.split()
        return [t.strip(".,!?;:") for t in tokens if len(t.strip(".,!?;:")) > 0]

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        scores = []

        for idx, doc in enumerate(self.documents):
            doc_vector = self.doc_vectors[idx]
            score = self._calculate_bm25_score(query_tokens, doc_vector)
            scores.append({
                "index": idx,
                "score": score,
                "document": doc
            })

        scores = sorted(scores, key=lambda x: x["score"], reverse=True)[:top_k]

        for result in scores:
            result.pop("index", None)
            result.pop("document", None)
            result.update(result.pop("document", {}))

        return scores

    def _calculate_bm25_score(self, query_tokens: List[str], doc_vector: Counter) -> float:
        score = 0.0
        doc_len = sum(doc_vector.values())

        for token in query_tokens:
            idf = self.idf.get(token, 0)
            tf = doc_vector.get(token, 0)

            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))

            score += idf * (numerator / denominator)

        return score

class KeywordSearch:
    def __init__(self, document_index: Optional[List[Dict[str, Any]]] = None):
        self.bm25 = None
        self.logger = get_logger(__name__)

        if document_index:
            self.build_index(document_index)

    def build_index(self, documents: List[Dict[str, Any]]):
        self.bm25 = BM25(documents)
        self.logger.info(f"Built keyword index with {len(documents)} documents")

    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        if not self.bm25:
            self.logger.warning("No index built for keyword search")
            return []

        try:
            results = self.bm25.search(query, top_k=top_k * 2)
            filtered_results = [
                result for result in results
                if result.get("score", 0) >= score_threshold
            ][:top_k]

            self.logger.info(f"Keyword search returned {len(filtered_results)} results")
            return filtered_results
        except Exception as e:
            self.logger.error(f"Error in keyword search: {e}")
            return []

    def search_by_keywords(self, keywords: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.bm25:
            return []

        query = " ".join(keywords)
        return self.search(query, top_k=top_k)

    def search_with_filters(self, query: str, metadata_filters: Dict[str, Any] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.search(query, top_k=top_k * 2)

        if metadata_filters:
            filtered = []
            for result in results:
                metadata = result.get("metadata", {})
                match = True

                for key, value in metadata_filters.items():
                    if metadata.get(key) != value:
                        match = False
                        break

                if match:
                    filtered.append(result)

            return filtered[:top_k]

        return results[:top_k]
