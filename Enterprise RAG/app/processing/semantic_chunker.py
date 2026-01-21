"""
Semantic Text Chunking - Preserve meaning while splitting documents
"""

import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class SemanticChunker:
    """
    Advanced chunking that preserves semantic units
    Respects sentence boundaries, paragraphs, and semantic meaning
    """

    def __init__(self, max_chunk_size: int = 1024, overlap: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> List[str]:
        """
        Split text into semantic chunks

        Args:
            text: Text to chunk
            max_chunk_size: Target chunk size

        Returns:
            List of text chunks
        """
        if not text or len(text) == 0:
            return []

        if len(text) <= self.max_chunk_size:
            return [text]

        # Split into paragraphs first
        paragraphs = self._split_paragraphs(text)

        # Then group paragraphs into chunks
        chunks = self._group_paragraphs(paragraphs)

        return chunks

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _group_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """Group paragraphs into chunks respecting size limits"""
        if not paragraphs:
            return []

        chunks = []
        current_chunk = ""
        last_chunk = ""

        for para in paragraphs:
            para_with_space = para + "\n\n"

            # If adding this paragraph exceeds limit
            if len(current_chunk) + len(para_with_space) > self.max_chunk_size:
                # Save current chunk
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    last_chunk = current_chunk

                # Start new chunk with overlap
                if self.overlap > 0 and last_chunk:
                    overlap_text = last_chunk[-self.overlap:]
                    current_chunk = overlap_text + "\n\n" + para_with_space
                else:
                    current_chunk = para_with_space
            else:
                current_chunk += para_with_space

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def chunk_by_sentences(self, text: str) -> List[str]:
        """
        Chunk by sentence boundaries
        Better for dense text like technical documentation
        """
        if not text or len(text) == 0:
            return []

        if len(text) <= self.max_chunk_size:
            return [text]

        # Split into sentences
        sentences = self._split_sentences(text)

        # Group sentences into chunks
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence_with_space = sentence + " "

            if len(current_chunk) + len(sentence_with_space) > self.max_chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # Add overlap from end of previous chunk
                if self.overlap > 0 and chunks:
                    overlap_text = chunks[-1][-self.overlap:]
                    current_chunk = overlap_text + " " + sentence_with_space
                else:
                    current_chunk = sentence_with_space
            else:
                current_chunk += sentence_with_space

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Handle abbreviations and ellipsis
        text = re.sub(r"([.!?])\s+(?=[A-Z])", r"\1|", text)
        text = re.sub(r"([.!?])\s+(?=['\"])", r"\1|", text)

        sentences = text.split("|")
        return [s.strip() for s in sentences if s.strip()]

    def chunk_by_heading(self, text: str, heading_marker: str = "#") -> List[str]:
        """
        Chunk by markdown headings
        Useful for structured documents

        Args:
            text: Text with markdown headings
            heading_marker: Character marking headings (# for markdown)

        Returns:
            List of chunks, each under a heading
        """
        if heading_marker != "#":
            # For other markers, treat as regular text
            return self.chunk(text)

        # Split by markdown headings
        pattern = r"^#+\s+"
        lines = text.split("\n")

        chunks = []
        current_chunk = ""
        current_heading = ""

        for line in lines:
            if re.match(pattern, line):
                # This is a heading
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                current_heading = line
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

                # Check if chunk is too large
                if len(current_chunk) > self.max_chunk_size:
                    chunks.append(current_chunk.strip())
                    # Keep heading for context
                    if current_heading:
                        current_chunk = current_heading + "\n"
                    else:
                        current_chunk = ""

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def chunk_by_code_blocks(self, text: str) -> List[str]:
        """
        Chunk while preserving code blocks
        Useful for documentation with code examples
        """
        # Pattern for code blocks (markdown or indented)
        code_block_pattern = r"```[\s\S]*?```|^    .*$"

        chunks = []
        current_chunk = ""

        # Split by both regular and code block boundaries
        parts = re.split(r"(```[\s\S]*?```)", text)

        for part in parts:
            if len(current_chunk) + len(part) <= self.max_chunk_size:
                current_chunk += part
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = part

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def get_chunk_stats(self, chunks: List[str]) -> dict:
        """Get statistics about chunks"""
        return {
            "num_chunks": len(chunks),
            "avg_size": sum(len(c) for c in chunks) // len(chunks) if chunks else 0,
            "min_size": min(len(c) for c in chunks) if chunks else 0,
            "max_size": max(len(c) for c in chunks) if chunks else 0,
            "total_chars": sum(len(c) for c in chunks),
        }
