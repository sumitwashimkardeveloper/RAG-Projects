from typing import List, Dict, Any
from dataclasses import dataclass
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class Chunk:
    content: str
    chunk_id: str
    source: str
    start_index: int
    end_index: int
    metadata: Dict[str, Any] = None

class TextChunker:
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, source: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        chunks = []
        metadata = metadata or {}

        words = text.split()
        current_chunk = []
        current_index = 0

        for idx, word in enumerate(words):
            current_chunk.append(word)

            if len(current_chunk) >= self.chunk_size:
                chunk_content = " ".join(current_chunk[:self.chunk_size])
                chunk_text = " ".join(current_chunk)

                chunk = Chunk(
                    content=chunk_text,
                    chunk_id=f"{source}_chunk_{len(chunks)}",
                    source=source,
                    start_index=current_index,
                    end_index=current_index + len(chunk_text),
                    metadata=metadata.copy()
                )
                chunks.append(chunk)

                overlap_words = current_chunk[self.chunk_size - self.overlap:]
                current_chunk = overlap_words
                current_index += len(chunk_text) - len(" ".join(overlap_words))

        if current_chunk:
            chunk_content = " ".join(current_chunk)
            chunk = Chunk(
                content=chunk_content,
                chunk_id=f"{source}_chunk_{len(chunks)}",
                source=source,
                start_index=current_index,
                end_index=current_index + len(chunk_content),
                metadata=metadata.copy()
            )
            chunks.append(chunk)

        logger.info(f"Chunked {source} into {len(chunks)} chunks")
        return chunks

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Chunk]:
        all_chunks = []

        for doc in documents:
            content = doc.get("content", "")
            source = doc.get("source", "unknown")
            metadata = doc.get("metadata", {})

            chunks = self.chunk_text(content, source, metadata)
            all_chunks.extend(chunks)

        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
