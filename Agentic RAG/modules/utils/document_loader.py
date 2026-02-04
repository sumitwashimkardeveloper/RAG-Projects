from typing import List, Dict, Any
from abc import ABC, abstractmethod
from pathlib import Path
import json
from modules.utils import get_logger

logger = get_logger(__name__)

class DocumentLoader(ABC):
    @abstractmethod
    def load(self, source: str) -> List[Dict[str, Any]]:
        pass

class TextFileLoader(DocumentLoader):
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return []

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return [{
                "content": content,
                "source": str(path),
                "metadata": {
                    "file_type": "text",
                    "file_size": path.stat().st_size,
                    "file_name": path.name
                }
            }]
        except Exception as e:
            logger.error(f"Error loading text file: {e}")
            return []

class PDFLoader(DocumentLoader):
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            try:
                import PyPDF2
            except ImportError:
                logger.warning("PyPDF2 not installed, skipping PDF loading")
                return []

            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return []

            documents = []
            with open(path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(pdf_reader.pages):
                    content = page.extract_text()
                    documents.append({
                        "content": content,
                        "source": str(path),
                        "metadata": {
                            "file_type": "pdf",
                            "page": page_num + 1,
                            "file_name": path.name,
                            "total_pages": len(pdf_reader.pages)
                        }
                    })

            logger.info(f"Loaded {len(documents)} pages from PDF: {file_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF: {e}")
            return []

class JSONLoader(DocumentLoader):
    def load(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return []

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                documents = []
                for idx, item in enumerate(data):
                    if isinstance(item, dict) and "content" in item:
                        documents.append({
                            "content": item.get("content", ""),
                            "source": f"{str(path)}_item_{idx}",
                            "metadata": {
                                "file_type": "json",
                                "index": idx,
                                "file_name": path.name,
                                **{k: v for k, v in item.items() if k != "content"}
                            }
                        })
                return documents
            else:
                return [{
                    "content": json.dumps(data),
                    "source": str(path),
                    "metadata": {
                        "file_type": "json",
                        "file_name": path.name
                    }
                }]
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
            return []

class DirectoryLoader(DocumentLoader):
    def __init__(self, extensions: List[str] = None):
        self.extensions = extensions or [".txt", ".pdf", ".json"]
        self.loaders = {
            ".txt": TextFileLoader(),
            ".pdf": PDFLoader(),
            ".json": JSONLoader()
        }

    def load(self, directory_path: str) -> List[Dict[str, Any]]:
        try:
            path = Path(directory_path)
            if not path.is_dir():
                logger.error(f"Directory not found: {directory_path}")
                return []

            all_documents = []
            for ext in self.extensions:
                if ext in self.loaders:
                    loader = self.loaders[ext]
                    for file_path in path.glob(f"*{ext}"):
                        documents = loader.load(str(file_path))
                        all_documents.extend(documents)

            logger.info(f"Loaded {len(all_documents)} documents from directory: {directory_path}")
            return all_documents
        except Exception as e:
            logger.error(f"Error loading directory: {e}")
            return []

def get_loader(file_path: str) -> DocumentLoader:
    path = Path(file_path)

    if path.is_dir():
        return DirectoryLoader()

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PDFLoader()
    elif suffix == ".json":
        return JSONLoader()
    elif suffix == ".txt":
        return TextFileLoader()
    else:
        return TextFileLoader()
