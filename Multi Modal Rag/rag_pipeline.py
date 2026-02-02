from typing import List, Dict, Any, Optional
import json

from indexer import MultiModalIndexer
from retriever import MultiModalRetriever
from config import Config

try:
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class RAGPrompts:
    @staticmethod
    def get_qa_prompt() -> str:
        return """Based on the following context from multiple media types (images, tables, charts, videos, audio transcripts, and documents), answer the question.

Context:
{context}

Question: {question}

Answer:"""

    @staticmethod
    def get_summary_prompt() -> str:
        return """Summarize the following multi-modal content, highlighting key information from different media types.

Content:
{context}

Summary:"""

    @staticmethod
    def get_analysis_prompt() -> str:
        return """Analyze the following multi-modal content and provide insights.

Media Types Found: {media_types}
Content:
{context}

Analysis:"""

    @staticmethod
    def get_comparison_prompt() -> str:
        return """Compare the information from different media types in the provided context.

{context}

Comparison:"""


class MultiModalRAGPipeline:
    def __init__(
        self,
        indexer: Optional[MultiModalIndexer] = None,
        retriever: Optional[MultiModalRetriever] = None,
        use_llm: bool = False
    ):
        self.config = Config()
        self.indexer = indexer or MultiModalIndexer(use_pinecone=False)
        self.retriever = retriever or MultiModalRetriever(
            vector_store=self.indexer.vector_store
        )
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE

        if self.use_llm and LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatOpenAI(
                    temperature=0.7,
                    model_name="gpt-3.5-turbo"
                )
            except Exception as e:
                print(f"LLM initialization failed: {e}")
                self.use_llm = False

    def index_files(self, file_paths: List[str]) -> Dict[str, Any]:
        return self.indexer.index_bulk_files(file_paths)

    def index_directory(self, directory_path: str) -> Dict[str, Any]:
        return self.indexer.index_directory(directory_path)

    def query(
        self,
        question: str,
        top_k: int = 5,
        media_type_filter: Optional[str] = None,
        use_llm: bool = True
    ) -> Dict[str, Any]:

        retrieval_result = self.retriever.retrieve(
            question,
            top_k=top_k,
            media_type_filter=media_type_filter
        )

        context = self._format_context(retrieval_result.documents)

        result = {
            "question": question,
            "retrieved_documents": len(retrieval_result.documents),
            "source_files": retrieval_result.source_files,
            "media_types": retrieval_result.media_types,
            "context": context,
            "confidence_scores": retrieval_result.confidence_scores
        }

        if use_llm and self.use_llm:
            answer = self._generate_answer(question, context)
            result["answer"] = answer
        else:
            result["answer"] = self._extract_top_content(retrieval_result.documents)

        return result

    def query_by_media_type(
        self,
        question: str,
        media_type: str,
        top_k: int = 5,
        use_llm: bool = True
    ) -> Dict[str, Any]:

        retrieval_result = self.retriever.retrieve_by_media_type(
            question,
            media_type,
            top_k
        )

        context = self._format_context(retrieval_result.documents)

        result = {
            "question": question,
            "media_type_filter": media_type,
            "retrieved_documents": len(retrieval_result.documents),
            "context": context
        }

        if use_llm and self.use_llm:
            answer = self._generate_answer(question, context)
            result["answer"] = answer
        else:
            result["answer"] = self._extract_top_content(retrieval_result.documents)

        return result

    def summarize(
        self,
        query: str,
        top_k: int = 5,
        use_llm: bool = True
    ) -> Dict[str, Any]:

        retrieval_result = self.retriever.retrieve(query, top_k)
        context = self._format_context(retrieval_result.documents)

        result = {
            "query": query,
            "retrieved_documents": len(retrieval_result.documents),
            "media_types": retrieval_result.media_types
        }

        if use_llm and self.use_llm:
            summary = self._generate_summary(context)
            result["summary"] = summary
        else:
            result["summary"] = self._extract_top_content(retrieval_result.documents, limit=3)

        return result

    def analyze(
        self,
        query: str,
        top_k: int = 5,
        use_llm: bool = True
    ) -> Dict[str, Any]:

        retrieval_result = self.retriever.retrieve(query, top_k)
        context = self._format_context(retrieval_result.documents)

        result = {
            "query": query,
            "retrieved_documents": len(retrieval_result.documents),
            "media_types": retrieval_result.media_types,
            "source_files": retrieval_result.source_files
        }

        if use_llm and self.use_llm:
            analysis = self._generate_analysis(context, retrieval_result.media_types)
            result["analysis"] = analysis
        else:
            result["analysis"] = self._extract_top_content(retrieval_result.documents, limit=5)

        return result

    def compare(
        self,
        query: str,
        top_k: int = 10,
        use_llm: bool = True
    ) -> Dict[str, Any]:

        retrieval_result = self.retriever.retrieve(query, top_k)
        context = self._format_context(retrieval_result.documents)

        result = {
            "query": query,
            "retrieved_documents": len(retrieval_result.documents),
            "comparison_sources": retrieval_result.source_files
        }

        if use_llm and self.use_llm:
            comparison = self._generate_comparison(context)
            result["comparison"] = comparison
        else:
            result["comparison"] = self._extract_top_content(retrieval_result.documents, limit=5)

        return result

    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        context_parts = []

        for idx, doc in enumerate(documents, 1):
            media_type = doc["metadata"].get("media_type", "unknown")
            file_name = doc["metadata"].get("file_name", "unknown")
            chunk_index = doc["metadata"].get("chunk_index", 0)

            context_parts.append(
                f"[{media_type.upper()}] {file_name} (Chunk {chunk_index}):\n{doc['content']}"
            )

        return "\n\n".join(context_parts)

    def _extract_top_content(
        self,
        documents: List[Dict[str, Any]],
        limit: int = 3
    ) -> str:
        top_docs = documents[:limit]
        return "\n\n".join([
            f"[{doc['metadata'].get('media_type', 'unknown').upper()}] {doc['content']}"
            for doc in top_docs
        ])

    def _generate_answer(self, question: str, context: str) -> str:
        if not self.use_llm:
            return "LLM not available"

        try:
            prompt = RAGPrompts.get_qa_prompt()
            response = self.llm.predict(
                prompt=prompt.format(context=context, question=question)
            )
            return response.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"

    def _generate_summary(self, context: str) -> str:
        if not self.use_llm:
            return "LLM not available"

        try:
            prompt = RAGPrompts.get_summary_prompt()
            response = self.llm.predict(prompt=prompt.format(context=context))
            return response.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def _generate_analysis(self, context: str, media_types: List[str]) -> str:
        if not self.use_llm:
            return "LLM not available"

        try:
            media_types_str = ", ".join(media_types)
            prompt = RAGPrompts.get_analysis_prompt()
            response = self.llm.predict(
                prompt=prompt.format(
                    context=context,
                    media_types=media_types_str
                )
            )
            return response.strip()
        except Exception as e:
            return f"Error generating analysis: {str(e)}"

    def _generate_comparison(self, context: str) -> str:
        if not self.use_llm:
            return "LLM not available"

        try:
            prompt = RAGPrompts.get_comparison_prompt()
            response = self.llm.predict(prompt=prompt.format(context=context))
            return response.strip()
        except Exception as e:
            return f"Error generating comparison: {str(e)}"

    def export_pipeline_config(self, output_path: str = "rag_pipeline_config.json"):
        config_data = {
            "embedding_model": self.config.EMBEDDING_MODEL,
            "embedding_dimension": self.config.EMBEDDING_DIMENSION,
            "chunk_size": self.config.CHUNK_SIZE,
            "chunk_overlap": self.config.CHUNK_OVERLAP,
            "supported_media_types": {
                "images": list(self.config.SUPPORTED_IMAGE_FORMATS),
                "videos": list(self.config.SUPPORTED_VIDEO_FORMATS),
                "audio": list(self.config.SUPPORTED_AUDIO_FORMATS),
                "documents": list(self.config.SUPPORTED_DOC_FORMATS)
            },
            "llm_enabled": self.use_llm
        }

        with open(output_path, 'w') as f:
            json.dump(config_data, f, indent=2)

        return output_path
