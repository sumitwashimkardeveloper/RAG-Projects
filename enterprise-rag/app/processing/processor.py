"""
Text Processing Pipeline
Combines cleaning, chunking, and tokenization
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.processing.cleaner import TextCleaner
from app.processing.semantic_chunker import SemanticChunker
from app.processing.tokenizer import TokenCounter

logger = logging.getLogger(__name__)


@dataclass
class ProcessedText:
    """Result of text processing"""

    original_text: str
    cleaned_text: str
    chunks: List[str]
    metadata: Dict[str, Any]


class TextProcessor:
    """
    Complete text processing pipeline
    Cleans, chunks, and tokenizes text
    """

    def __init__(
        self,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
        remove_urls: bool = True,
        remove_emails: bool = False,
        remove_html: bool = True,
        remove_markdown: bool = False,
        model: str = "gpt-4",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_html = remove_html
        self.remove_markdown = remove_markdown
        self.model = model

        self.chunker = SemanticChunker(
            max_chunk_size=chunk_size, overlap=chunk_overlap
        )
        self.token_counter = TokenCounter()

    def process(
        self,
        text: str,
        strategy: str = "semantic",
    ) -> ProcessedText:
        """
        Process text through complete pipeline

        Args:
            text: Raw text to process
            strategy: Chunking strategy (semantic, sentence, heading, code)

        Returns:
            ProcessedText with cleaned text, chunks, and metadata
        """
        if not text:
            return ProcessedText(
                original_text="",
                cleaned_text="",
                chunks=[],
                metadata={"error": "Empty input"},
            )

        # Step 1: Clean text
        cleaned_text = self._clean_text(text)

        if not cleaned_text:
            return ProcessedText(
                original_text=text,
                cleaned_text=cleaned_text,
                chunks=[],
                metadata={"error": "Text became empty after cleaning"},
            )

        # Step 2: Chunk text
        chunks = self._chunk_text(cleaned_text, strategy)

        # Step 3: Generate metadata
        metadata = self._generate_metadata(text, cleaned_text, chunks)

        return ProcessedText(
            original_text=text,
            cleaned_text=cleaned_text,
            chunks=chunks,
            metadata=metadata,
        )

    def _clean_text(self, text: str) -> str:
        """Clean text according to settings"""
        cleaned = TextCleaner.clean(
            text, remove_urls=self.remove_urls, remove_emails=self.remove_emails
        )

        if self.remove_html:
            cleaned = TextCleaner.remove_html_tags(cleaned)

        if self.remove_markdown:
            cleaned = TextCleaner.remove_markdown_formatting(cleaned)

        return cleaned

    def _chunk_text(self, text: str, strategy: str) -> List[str]:
        """Chunk text using specified strategy"""
        if strategy == "sentence":
            return self.chunker.chunk_by_sentences(text)
        elif strategy == "heading":
            return self.chunker.chunk_by_heading(text)
        elif strategy == "code":
            return self.chunker.chunk_by_code_blocks(text)
        else:  # semantic (default)
            return self.chunker.chunk(text)

    def _generate_metadata(
        self, original: str, cleaned: str, chunks: List[str]
    ) -> Dict[str, Any]:
        """Generate metadata about processing"""
        total_tokens = self.token_counter.count_tokens(cleaned, self.model)
        chunk_tokens = [
            self.token_counter.count_tokens(chunk, self.model) for chunk in chunks
        ]

        return {
            "original_length": len(original),
            "cleaned_length": len(cleaned),
            "total_tokens": total_tokens,
            "num_chunks": len(chunks),
            "avg_chunk_size": sum(len(c) for c in chunks) // len(chunks)
            if chunks
            else 0,
            "max_chunk_size": max(len(c) for c in chunks) if chunks else 0,
            "min_chunk_size": min(len(c) for c in chunks) if chunks else 0,
            "avg_chunk_tokens": sum(chunk_tokens) // len(chunk_tokens)
            if chunk_tokens
            else 0,
            "max_chunk_tokens": max(chunk_tokens) if chunk_tokens else 0,
            "words": self.token_counter.count_words(cleaned),
            "sentences": self.token_counter.count_sentences(cleaned),
            "compression_ratio": (
                len(cleaned) / len(original) if original else 1
            ),
        }

    def validate_chunks(
        self, chunks: List[str], max_tokens: int = 8000
    ) -> Dict[str, Any]:
        """
        Validate chunks for compatibility with LLM

        Args:
            chunks: Text chunks to validate
            max_tokens: Maximum tokens allowed per chunk

        Returns:
            Validation report
        """
        report = {
            "total_chunks": len(chunks),
            "valid_chunks": 0,
            "oversized_chunks": [],
            "undersized_chunks": [],
            "token_distribution": [],
        }

        for idx, chunk in enumerate(chunks):
            tokens = self.token_counter.count_tokens(chunk, self.model)
            report["token_distribution"].append(tokens)

            if tokens > max_tokens:
                report["oversized_chunks"].append({"index": idx, "tokens": tokens})
            elif tokens < 10:  # Too small
                report["undersized_chunks"].append({"index": idx, "tokens": tokens})
            else:
                report["valid_chunks"] += 1

        return report

    def merge_small_chunks(self, chunks: List[str], min_size: int = 100) -> List[str]:
        """
        Merge chunks that are too small

        Args:
            chunks: List of chunks
            min_size: Minimum chunk size

        Returns:
            Merged chunks
        """
        if not chunks:
            return []

        merged = []
        current = ""

        for chunk in chunks:
            if len(current) + len(chunk) <= self.chunk_size:
                current += " " + chunk if current else chunk
            else:
                if current:
                    merged.append(current)
                current = chunk

        if current:
            merged.append(current)

        return merged

    def split_oversized_chunks(
        self, chunks: List[str], max_size: int = None
    ) -> List[str]:
        """
        Split chunks that exceed size limit

        Args:
            chunks: List of chunks
            max_size: Maximum chunk size

        Returns:
            Split chunks
        """
        if max_size is None:
            max_size = self.chunk_size

        split_chunks = []

        for chunk in chunks:
            if len(chunk) <= max_size:
                split_chunks.append(chunk)
            else:
                # Split oversized chunk
                sub_chunks = self.chunker.chunk_by_sentences(chunk)
                split_chunks.extend(sub_chunks)

        return split_chunks

    def add_metadata_to_chunks(
        self, chunks: List[str], doc_title: str, doc_source: str
    ) -> List[Dict[str, Any]]:
        """
        Add metadata to each chunk

        Args:
            chunks: Text chunks
            doc_title: Document title
            doc_source: Document source

        Returns:
            Chunks with metadata
        """
        enriched = []

        for idx, chunk in enumerate(chunks):
            tokens = self.token_counter.count_tokens(chunk, self.model)

            enriched.append(
                {
                    "content": chunk,
                    "chunk_index": idx,
                    "document_title": doc_title,
                    "document_source": doc_source,
                    "token_count": tokens,
                    "character_count": len(chunk),
                    "word_count": self.token_counter.count_words(chunk),
                }
            )

        return enriched
