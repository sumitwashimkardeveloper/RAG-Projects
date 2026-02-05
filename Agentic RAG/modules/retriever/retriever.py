from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from modules.utils import get_logger, get_database_manager, get_embeddings
from .semantic_search import SemanticSearch
from .keyword_search import KeywordSearch
from .hybrid_search import HybridSearch
from .ranking import RankingEngine, ScoreNormalizer, ResultScorer
from .filtering import Deduplicator, ResultFilter, FilterPipeline

logger = get_logger(__name__)

@dataclass
class Document:
    content: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    relevance_score: float = 0.0
    rank: int = 0

@dataclass
class RetrievalResult:
    query: str
    documents: List[Document]
    total_retrieved: int
    search_strategy: str = "hybrid"
    metadata: Dict[str, Any] = field(default_factory=dict)

class Retriever:
    def __init__(self, config=None, db_manager=None):
        self.config = config
        self.logger = get_logger(__name__)
        self.db_manager = db_manager or get_database_manager(config)

        self._initialize_search_components()

    def _initialize_search_components(self):
        vector_store = self.db_manager.get_vector_store()
        embeddings_provider = self.config.get("llm.provider", "openai") if self.config else "openai"

        self.semantic_searcher = SemanticSearch(vector_store, embeddings_provider) if vector_store else None
        self.keyword_searcher = KeywordSearch()
        self.hybrid_searcher = HybridSearch(self.semantic_searcher, self.keyword_searcher)

        self.ranking_engine = RankingEngine()
        self.filter_pipeline = FilterPipeline()

    def retrieve(self, query: str, top_k: int = 5, strategy: str = "hybrid") -> RetrievalResult:
        self.logger.info(f"Retrieving with strategy: {strategy}")

        if strategy == "semantic":
            results = self.semantic_search(query, top_k=top_k)
        elif strategy == "keyword":
            results = self.keyword_search(query, top_k=top_k)
        else:
            results = self.hybrid_search(query, top_k=top_k)

        results = self.deduplicate(results)
        results = self._apply_filtering(results)
        results = self.rank_results(results, query)
        results = results[:top_k]

        documents = self._convert_to_documents(results)

        return RetrievalResult(
            query=query,
            documents=documents,
            total_retrieved=len(documents),
            search_strategy=strategy,
            metadata={
                "raw_result_count": len(results),
                "strategy": strategy
            }
        )

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.semantic_searcher:
            self.logger.warning("Semantic searcher not initialized")
            return []

        return self.semantic_searcher.search(query, top_k=top_k)

    def keyword_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.keyword_searcher:
            self.logger.warning("Keyword searcher not initialized")
            return []

        return self.keyword_searcher.search(query, top_k=top_k)

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self.hybrid_searcher:
            self.logger.warning("Hybrid searcher not initialized")
            return []

        return self.hybrid_searcher.search(query, top_k=top_k)

    def rank_results(self, results: List[Dict[str, Any]], query: str = "") -> List[Dict[str, Any]]:
        if not results:
            return results

        normalized = ScoreNormalizer.normalize_minmax(results)

        results_with_rank = []
        for rank, result in enumerate(normalized, 1):
            result["rank"] = rank
            results_with_rank.append(result)

        return sorted(results_with_rank, key=lambda x: x.get("score", 0), reverse=True)

    def deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return Deduplicator.deduplicate_by_id(results)

    def filter_results(self, results: List[Dict[str, Any]],
                      score_threshold: float = 0.0,
                      metadata_filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        filtered = ResultFilter.filter_by_score(results, score_threshold)

        if metadata_filters:
            filtered = ResultFilter.filter_by_metadata(filtered, metadata_filters)

        return filtered

    def _apply_filtering(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.config:
            score_threshold = self.config.get("retriever.score_threshold", 0.0)
            results = ResultFilter.filter_by_score(results, score_threshold)

        return results

    def _convert_to_documents(self, results: List[Dict[str, Any]]) -> List[Document]:
        documents = []
        for idx, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            document = Document(
                content=metadata.get("content", "")[:500],
                source=metadata.get("source", "unknown"),
                metadata=metadata,
                relevance_score=result.get("score", 0),
                rank=idx
            )
            documents.append(document)

        return documents

    def set_retrieval_config(self, top_k: int = 5, score_threshold: float = 0.0):
        if self.config:
            self.config.get = lambda key, default=None: {
                "retriever.top_k": top_k,
                "retriever.score_threshold": score_threshold
            }.get(key, default)

        self.logger.info(f"Set retrieval config: top_k={top_k}, threshold={score_threshold}")
