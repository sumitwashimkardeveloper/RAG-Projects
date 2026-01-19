"""
Document Chunking - Split documents into manageable pieces for embedding
"""

from typing import List
import logging

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Chunks documents into overlapping segments for embedding
    Preserves semantic meaning while keeping chunks within token limits
    """

    def __init__(self):
        pass

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
        separator: str = "\n",
    ) -> List[str]:
        """
        Chunk text into overlapping segments

        Args:
            text: Text to chunk
            chunk_size: Target size of each chunk (approximate chars)
            chunk_overlap: Characters to overlap between chunks
            separator: Delimiter to respect when chunking

        Returns:
            List of text chunks
        """
        if not text or len(text) == 0:
            return []

        # Clean text
        text = text.strip()

        # For small text, return as-is
        if len(text) <= chunk_size:
            return [text]

        # Split by separator first to respect structure
        segments = text.split(separator)

        chunks = []
        current_chunk = ""

        for segment in segments:
            # Add separator back
            segment_with_sep = segment + separator

            # If adding this segment exceeds chunk size
            if len(current_chunk) + len(segment_with_sep) > chunk_size:
                # Save current chunk if not empty
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # Start new chunk with overlap from previous
                if chunks and chunk_overlap > 0:
                    # Take last chunk_overlap chars from previous chunk
                    overlap_text = chunks[-1][-chunk_overlap:] if len(chunks[-1]) >= chunk_overlap else chunks[-1]
                    current_chunk = overlap_text + separator + segment_with_sep
                else:
                    current_chunk = segment_with_sep
            else:
                current_chunk += segment_with_sep

        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        logger.debug(f"Chunked text into {len(chunks)} segments")
        return chunks

    def chunk_by_sentence(
        self,
        text: str,
        chunk_size: int = 1024,
        chunk_overlap: int = 200,
    ) -> List[str]:
        """
        Chunk text by sentences for better semantic preservation

        Args:
            text: Text to chunk
            chunk_size: Target size per chunk
            chunk_overlap: Overlap size

        Returns:
            List of text chunks
        """
        # Simple sentence splitting (for production, use more sophisticated approach)
        sentences = text.replace("!", ".").replace("?", ".").split(".")
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return [text] if text else []

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            sentence_with_period = sentence + ". "

            if len(current_chunk) + len(sentence_with_period) > chunk_size:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                # Add overlap
                if chunks and chunk_overlap > 0:
                    overlap_text = chunks[-1][-chunk_overlap:]
                    current_chunk = overlap_text + " " + sentence_with_period
                else:
                    current_chunk = sentence_with_period
            else:
                current_chunk += sentence_with_period

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        logger.debug(f"Chunked text into {len(chunks)} sentence-based segments")
        return chunks

    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of token count (1 token ≈ 4 chars)

        Args:
            text: Text to estimate

        Returns:
            Approximate token count
        """
        return len(text) // 4
