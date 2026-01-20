"""
Text Processing API Endpoints
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.processing import TextProcessor, TextCleaner

router = APIRouter(prefix="/api/v1/processing", tags=["Processing"])


class CleanRequest(BaseModel):
    text: str
    remove_urls: bool = True
    remove_emails: bool = False
    remove_html: bool = True
    remove_markdown: bool = False


class ChunkRequest(BaseModel):
    text: str
    chunk_size: int = 1024
    chunk_overlap: int = 200
    strategy: str = "semantic"  # semantic, sentence, heading, code
    model: str = "gpt-4"


class ProcessRequest(BaseModel):
    text: str
    chunk_size: int = 1024
    chunk_overlap: int = 200
    strategy: str = "semantic"
    remove_urls: bool = True
    remove_emails: bool = False
    remove_html: bool = True
    remove_markdown: bool = False
    model: str = "gpt-4"


@router.post("/clean")
async def clean_text(request: CleanRequest):
    """
    Clean and normalize text

    Args:
        text: Text to clean
        remove_urls: Remove URLs
        remove_emails: Remove emails
        remove_html: Remove HTML tags
        remove_markdown: Remove markdown formatting

    Returns:
        Cleaned text
    """
    try:
        cleaned = TextCleaner.clean(
            request.text,
            remove_urls=request.remove_urls,
            remove_emails=request.remove_emails,
        )

        if request.remove_html:
            cleaned = TextCleaner.remove_html_tags(cleaned)

        if request.remove_markdown:
            cleaned = TextCleaner.remove_markdown_formatting(cleaned)

        return {
            "original_length": len(request.text),
            "cleaned_length": len(cleaned),
            "text": cleaned,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chunk")
async def chunk_text(request: ChunkRequest):
    """
    Chunk text into segments

    Args:
        text: Text to chunk
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        strategy: Chunking strategy
        model: Model for token counting

    Returns:
        List of chunks with metadata
    """
    try:
        processor = TextProcessor(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            model=request.model,
        )

        # Use only chunking
        from app.processing import SemanticChunker

        chunker = SemanticChunker(
            max_chunk_size=request.chunk_size, overlap=request.chunk_overlap
        )

        if request.strategy == "sentence":
            chunks = chunker.chunk_by_sentences(request.text)
        elif request.strategy == "heading":
            chunks = chunker.chunk_by_heading(request.text)
        elif request.strategy == "code":
            chunks = chunker.chunk_by_code_blocks(request.text)
        else:
            chunks = chunker.chunk(request.text)

        stats = chunker.get_chunk_stats(chunks)

        return {
            "num_chunks": len(chunks),
            "chunks": chunks,
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
async def process_text(request: ProcessRequest):
    """
    Full text processing pipeline
    Cleans, chunks, and tokenizes text

    Args:
        text: Text to process
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks
        strategy: Chunking strategy
        remove_urls: Remove URLs
        remove_emails: Remove emails
        remove_html: Remove HTML
        remove_markdown: Remove markdown
        model: LLM model for tokenization

    Returns:
        Processed text with chunks and metadata
    """
    try:
        processor = TextProcessor(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            remove_urls=request.remove_urls,
            remove_emails=request.remove_emails,
            remove_html=request.remove_html,
            remove_markdown=request.remove_markdown,
            model=request.model,
        )

        result = processor.process(request.text, strategy=request.strategy)

        return {
            "original_length": result.metadata["original_length"],
            "cleaned_length": result.metadata["cleaned_length"],
            "num_chunks": len(result.chunks),
            "chunks": result.chunks,
            "metadata": result.metadata,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_chunks(chunks: List[str], max_tokens: int = 8000, model: str = "gpt-4"):
    """
    Validate chunks for LLM compatibility

    Args:
        chunks: Text chunks to validate
        max_tokens: Maximum tokens per chunk
        model: LLM model

    Returns:
        Validation report
    """
    try:
        processor = TextProcessor(model=model)
        report = processor.validate_chunks(chunks, max_tokens=max_tokens)

        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merge")
async def merge_chunks(chunks: List[str], min_size: int = 100, chunk_size: int = 1024):
    """
    Merge small chunks

    Args:
        chunks: Chunks to merge
        min_size: Minimum chunk size
        chunk_size: Target chunk size

    Returns:
        Merged chunks
    """
    try:
        processor = TextProcessor(chunk_size=chunk_size)
        merged = processor.merge_small_chunks(chunks, min_size=min_size)

        return {"original_count": len(chunks), "merged_count": len(merged), "chunks": merged}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/split")
async def split_chunks(chunks: List[str], max_size: int = 1024):
    """
    Split oversized chunks

    Args:
        chunks: Chunks to split
        max_size: Maximum chunk size

    Returns:
        Split chunks
    """
    try:
        processor = TextProcessor(chunk_size=max_size)
        split = processor.split_oversized_chunks(chunks, max_size=max_size)

        return {
            "original_count": len(chunks),
            "split_count": len(split),
            "chunks": split,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enrich")
async def enrich_chunks(
    chunks: List[str], doc_title: str, doc_source: str, model: str = "gpt-4"
):
    """
    Add metadata to chunks

    Args:
        chunks: Text chunks
        doc_title: Document title
        doc_source: Document source
        model: LLM model

    Returns:
        Chunks with metadata
    """
    try:
        processor = TextProcessor(model=model)
        enriched = processor.add_metadata_to_chunks(chunks, doc_title, doc_source)

        return {"count": len(enriched), "chunks": enriched}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
