from typing import List, Dict, Any, Optional
from modules.utils import get_logger, get_embeddings, VectorStore

logger = get_logger(__name__)

class SemanticSearch:
    def __init__(self, vector_store: VectorStore, embeddings_provider: str = "openai"):
        self.vector_store = vector_store
        self.embeddings = get_embeddings(provider=embeddings_provider)
        self.logger = get_logger(__name__)

    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.0) -> List[Dict[str, Any]]:
        try:
            query_embedding = self.embeddings.embed_text(query)
            results = self.vector_store.search(query_embedding, top_k=top_k)

            filtered_results = [
                result for result in results
                if result.get("score", 0) >= score_threshold
            ]

            self.logger.info(f"Semantic search returned {len(filtered_results)} results for query")
            return filtered_results
        except Exception as e:
            self.logger.error(f"Error in semantic search: {e}")
            return []

    def batch_search(self, queries: List[str], top_k: int = 5) -> List[List[Dict[str, Any]]]:
        all_results = []
        for query in queries:
            results = self.search(query, top_k=top_k)
            all_results.append(results)
        return all_results

    def search_with_reranking(self, query: str, top_k: int = 5, rerank_top_n: int = None) -> List[Dict[str, Any]]:
        if rerank_top_n is None:
            rerank_top_n = top_k

        initial_results = self.search(query, top_k=rerank_top_n * 2)

        if not initial_results:
            return []

        query_embedding = self.embeddings.embed_text(query)
        rescored = []

        for result in initial_results[:rerank_top_n]:
            try:
                doc_embedding = result.get("embedding", [])
                if doc_embedding:
                    similarity = self._cosine_similarity(query_embedding, doc_embedding)
                    result["reranked_score"] = similarity
                    rescored.append(result)
                else:
                    rescored.append(result)
            except Exception as e:
                self.logger.warning(f"Error reranking result: {e}")
                rescored.append(result)

        return sorted(rescored, key=lambda x: x.get("reranked_score", x.get("score", 0)), reverse=True)[:top_k]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a ** 2 for a in vec1) ** 0.5
        magnitude2 = sum(b ** 2 for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)
