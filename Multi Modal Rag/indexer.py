import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from media_processors import MediaProcessorFactory
from vector_store import VectorStore
from config import Config

class MultiModalIndexer:
    def __init__(self, use_pinecone: bool = True):
        self.config = Config()
        self.vector_store = VectorStore(use_pinecone=use_pinecone)
        self.processed_files = {}

    def index_directory(self, directory_path: str) -> Dict[str, Any]:
        directory_path = Path(directory_path)

        if not directory_path.exists():
            return {"error": f"Directory not found: {directory_path}"}

        results = {
            "total_files": 0,
            "successfully_indexed": 0,
            "failed_files": [],
            "media_type_breakdown": {},
            "total_chunks_created": 0
        }

        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                result = self.index_file(str(file_path))
                results["total_files"] += 1

                if result.get("status") == "success":
                    results["successfully_indexed"] += 1
                    media_type = result.get("media_type")
                    if media_type:
                        results["media_type_breakdown"][media_type] = \
                            results["media_type_breakdown"].get(media_type, 0) + 1
                    results["total_chunks_created"] += result.get("chunks_count", 0)
                else:
                    results["failed_files"].append({
                        "file": str(file_path),
                        "error": result.get("error")
                    })

        return results

    def index_file(self, file_path: str) -> Dict[str, Any]:
        file_path = str(Path(file_path))

        if file_path in self.processed_files:
            return {
                "status": "skipped",
                "message": "File already indexed"
            }

        processor = MediaProcessorFactory.get_processor(file_path)

        if processor is None:
            return {
                "status": "error",
                "error": f"Unsupported file type: {Path(file_path).suffix}"
            }

        try:
            processed_data = processor.process(file_path)

            chunks = processed_data.get("chunks", [])
            if not chunks and processed_data.get("text_content"):
                chunks = processor.chunk_content(processed_data.get("text_content", ""))

            documents_to_add = []

            for chunk_idx, chunk_text in enumerate(chunks):
                if chunk_text.strip():
                    doc_data = {
                        "content": chunk_text,
                        "media_type": processed_data.get("type", "unknown"),
                        "file_path": file_path,
                        "chunk_index": chunk_idx,
                        "metadata": {
                            "file_name": Path(file_path).name,
                            "media_type": processed_data.get("type"),
                            **processed_data.get("metadata", {})
                        }
                    }

                    if processed_data.get("type") == "image":
                        doc_data["metadata"]["objects"] = processed_data.get("objects", {})
                    elif processed_data.get("type") == "video":
                        doc_data["metadata"]["frame_count"] = len(processed_data.get("frames", []))
                    elif processed_data.get("type") == "audio":
                        doc_data["metadata"]["features"] = processed_data.get("audio_features", {})
                    elif processed_data.get("type") == "powerpoint":
                        doc_data["metadata"]["slide_count"] = len(processed_data.get("slides", []))

                    documents_to_add.append(doc_data)

            added_doc_ids = self.vector_store.add_documents(documents_to_add)

            self.processed_files[file_path] = {
                "media_type": processed_data.get("type"),
                "chunks_count": len(chunks),
                "doc_ids": added_doc_ids
            }

            return {
                "status": "success",
                "file": file_path,
                "media_type": processed_data.get("type"),
                "chunks_count": len(added_doc_ids),
                "doc_ids": added_doc_ids
            }

        except Exception as e:
            return {
                "status": "error",
                "file": file_path,
                "error": str(e)
            }

    def index_bulk_files(self, file_paths: List[str]) -> Dict[str, Any]:
        results = {
            "total_files": len(file_paths),
            "successfully_indexed": 0,
            "failed_files": [],
            "media_type_breakdown": {},
            "total_chunks_created": 0
        }

        for file_path in file_paths:
            result = self.index_file(file_path)

            if result.get("status") == "success":
                results["successfully_indexed"] += 1
                media_type = result.get("media_type")
                if media_type:
                    results["media_type_breakdown"][media_type] = \
                        results["media_type_breakdown"].get(media_type, 0) + 1
                results["total_chunks_created"] += result.get("chunks_count", 0)
            else:
                results["failed_files"].append({
                    "file": file_path,
                    "error": result.get("error")
                })

        return results

    def reindex_file(self, file_path: str) -> Dict[str, Any]:
        file_path = str(Path(file_path))

        doc_ids = self.processed_files.get(file_path, {}).get("doc_ids", [])
        self.vector_store.delete_by_file_path(file_path)
        del self.processed_files[file_path]

        return self.index_file(file_path)

    def remove_file(self, file_path: str) -> Dict[str, Any]:
        file_path = str(Path(file_path))

        deleted_count = self.vector_store.delete_by_file_path(file_path)

        if file_path in self.processed_files:
            del self.processed_files[file_path]

        return {
            "status": "success",
            "file": file_path,
            "deleted_documents": deleted_count
        }

    def get_indexed_files(self) -> List[str]:
        return list(self.processed_files.keys())

    def get_indexing_statistics(self) -> Dict[str, Any]:
        vector_stats = self.vector_store.get_statistics()

        return {
            "indexed_files": len(self.processed_files),
            "files_breakdown": {
                file_path: info for file_path, info in self.processed_files.items()
            },
            "vector_store": vector_stats
        }

    def export_index_metadata(self, output_path: str):
        metadata = {
            "indexed_files": self.get_indexed_files(),
            "statistics": self.get_indexing_statistics(),
            "config": {
                "chunk_size": self.config.CHUNK_SIZE,
                "chunk_overlap": self.config.CHUNK_OVERLAP,
                "embedding_model": self.config.EMBEDDING_MODEL
            }
        }

        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return output_path
