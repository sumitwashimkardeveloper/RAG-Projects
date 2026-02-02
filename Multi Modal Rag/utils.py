import os
from typing import List, Dict, Any
from pathlib import Path
import shutil
import json
from datetime import datetime

from config import Config

class FileUtils:
    @staticmethod
    def get_supported_files(directory: str) -> List[str]:
        config = Config()
        supported_extensions = (
            config.SUPPORTED_IMAGE_FORMATS |
            config.SUPPORTED_VIDEO_FORMATS |
            config.SUPPORTED_AUDIO_FORMATS |
            config.SUPPORTED_DOC_FORMATS |
            {".csv", ".xlsx"}
        )

        supported_files = []
        for file_path in Path(directory).rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                supported_files.append(str(file_path))

        return supported_files

    @staticmethod
    def get_unsupported_files(directory: str) -> List[str]:
        config = Config()
        supported_extensions = (
            config.SUPPORTED_IMAGE_FORMATS |
            config.SUPPORTED_VIDEO_FORMATS |
            config.SUPPORTED_AUDIO_FORMATS |
            config.SUPPORTED_DOC_FORMATS |
            {".csv", ".xlsx"}
        )

        unsupported_files = []
        for file_path in Path(directory).rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() not in supported_extensions:
                unsupported_files.append(str(file_path))

        return unsupported_files

    @staticmethod
    def cleanup_temp_files():
        config = Config()
        if os.path.exists(config.TEMP_DIR):
            shutil.rmtree(config.TEMP_DIR)
            os.makedirs(config.TEMP_DIR, exist_ok=True)

    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        return os.path.getsize(file_path) / (1024 * 1024)

    @staticmethod
    def is_file_supported(file_path: str) -> bool:
        config = Config()
        ext = Path(file_path).suffix.lower()

        supported_extensions = (
            config.SUPPORTED_IMAGE_FORMATS |
            config.SUPPORTED_VIDEO_FORMATS |
            config.SUPPORTED_AUDIO_FORMATS |
            config.SUPPORTED_DOC_FORMATS |
            {".csv", ".xlsx"}
        )

        return ext in supported_extensions


class TextUtils:
    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    @staticmethod
    def calculate_token_estimate(text: str, tokens_per_word: float = 1.3) -> int:
        word_count = len(text.split())
        return int(word_count * tokens_per_word)

    @staticmethod
    def merge_texts(texts: List[str], separator: str = " ") -> str:
        return separator.join([t.strip() for t in texts if t.strip()])

    @staticmethod
    def clean_text(text: str) -> str:
        text = text.strip()
        text = " ".join(text.split())
        return text


class PerformanceUtils:
    @staticmethod
    def estimate_indexing_time(file_count: int, avg_file_size_mb: float) -> Dict[str, Any]:
        base_time_per_file = 0.5
        time_per_mb = 0.1

        estimated_seconds = (file_count * base_time_per_file) + (file_count * avg_file_size_mb * time_per_mb)

        hours = estimated_seconds // 3600
        minutes = (estimated_seconds % 3600) // 60
        seconds = estimated_seconds % 60

        return {
            "estimated_seconds": estimated_seconds,
            "estimated_time": f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}",
            "per_file_seconds": estimated_seconds / file_count if file_count > 0 else 0
        }

    @staticmethod
    def estimate_retrieval_time(query_complexity: str = "simple") -> Dict[str, float]:
        base_times = {
            "simple": 0.1,
            "moderate": 0.5,
            "complex": 1.0
        }

        return {
            "estimated_seconds": base_times.get(query_complexity, 0.1),
            "query_complexity": query_complexity
        }


class ReportGenerator:
    @staticmethod
    def generate_indexing_report(indexing_result: Dict[str, Any], output_path: str = "indexing_report.json"):
        report = {
            "timestamp": datetime.now().isoformat(),
            "indexing_results": indexing_result,
            "summary": {
                "total_files_processed": indexing_result.get("total_files", 0),
                "successful_indexing_rate": (
                    indexing_result.get("successfully_indexed", 0) /
                    indexing_result.get("total_files", 1) * 100
                ),
                "total_chunks_created": indexing_result.get("total_chunks_created", 0),
                "media_type_distribution": indexing_result.get("media_type_breakdown", {})
            }
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return output_path

    @staticmethod
    def generate_retrieval_report(
        retrieval_results: List[Dict[str, Any]],
        output_path: str = "retrieval_report.json"
    ):
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_queries": len(retrieval_results),
            "queries": retrieval_results,
            "statistics": {
                "avg_results_per_query": sum(
                    len(r.get("documents", [])) for r in retrieval_results
                ) / len(retrieval_results) if retrieval_results else 0,
                "avg_confidence": sum(
                    sum(r.get("confidence_scores", [])) / len(r.get("confidence_scores", [1]))
                    for r in retrieval_results
                ) / len(retrieval_results) if retrieval_results else 0
            }
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return output_path

    @staticmethod
    def generate_system_health_report(stats: Dict[str, Any], output_path: str = "health_report.json"):
        report = {
            "timestamp": datetime.now().isoformat(),
            "vector_store_health": {
                "total_documents": stats.get("vector_store", {}).get("total_documents", 0),
                "total_chunks": stats.get("vector_store", {}).get("total_chunks", 0),
                "media_types_supported": len(stats.get("vector_store", {}).get("media_type_distribution", {}))
            },
            "configuration": {
                "embedding_model": stats.get("retriever_info", {}).get("embedding_model", ""),
                "embedding_dimension": stats.get("retriever_info", {}).get("embedding_dimension", 0)
            }
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        return output_path


class ValidationUtils:
    @staticmethod
    def validate_directory(directory: str) -> Dict[str, Any]:
        path = Path(directory)

        if not path.exists():
            return {"valid": False, "error": "Directory does not exist"}

        if not path.is_dir():
            return {"valid": False, "error": "Path is not a directory"}

        try:
            files = list(path.rglob("*"))
            supported = FileUtils.get_supported_files(directory)

            return {
                "valid": True,
                "total_items": len(files),
                "supported_files": len(supported),
                "unsupported_files": len(files) - len(supported),
                "path": str(path.absolute())
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def validate_file(file_path: str) -> Dict[str, Any]:
        path = Path(file_path)

        if not path.exists():
            return {"valid": False, "error": "File does not exist"}

        if not path.is_file():
            return {"valid": False, "error": "Path is not a file"}

        if not FileUtils.is_file_supported(file_path):
            return {
                "valid": False,
                "error": f"File type {path.suffix} is not supported"
            }

        try:
            file_size_mb = FileUtils.get_file_size_mb(file_path)

            return {
                "valid": True,
                "file_name": path.name,
                "file_type": path.suffix,
                "file_size_mb": file_size_mb,
                "path": str(path.absolute())
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}
