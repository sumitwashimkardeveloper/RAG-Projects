"""
File-based Data Source Connector
Handles local files: PDF, DOCX, Excel, CSV, etc.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

from app.connectors.base import BaseConnector, DocumentMetadata
from app.document_processors import (
    PDFProcessor,
    DOCXProcessor,
    ExcelProcessor,
    CSVProcessor,
    MarkdownProcessor,
    PlainTextProcessor,
)

logger = logging.getLogger(__name__)


class FileConnector(BaseConnector):
    """
    Connector for file-based documents
    Supports PDF, DOCX, XLSX, CSV, Markdown, etc.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.processors = {
            ".pdf": PDFProcessor(),
            ".docx": DOCXProcessor(),
            ".xlsx": ExcelProcessor(),
            ".xls": ExcelProcessor(),
            ".csv": CSVProcessor(),
            ".md": MarkdownProcessor(),
            ".markdown": MarkdownProcessor(),
            ".txt": PlainTextProcessor(),
        }

    def _validate_config(self):
        """Validate required file configuration"""
        if "directory" not in self.config and "file_path" not in self.config:
            raise ValueError("Must provide either 'directory' or 'file_path'")

    def test_connection(self) -> bool:
        """Test if files/directory is accessible"""
        try:
            if "file_path" in self.config:
                path = Path(self.config["file_path"])
                return path.exists() and path.is_file()
            else:
                path = Path(self.config["directory"])
                return path.exists() and path.is_dir()
        except Exception as e:
            self.logger.error(f"File access failed: {str(e)}")
            return False

    def get_documents(self) -> List[DocumentMetadata]:
        """
        Retrieve all documents from files
        """
        documents = []

        if "file_path" in self.config:
            path = Path(self.config["file_path"])
            doc = self._process_file(path)
            if doc:
                documents.append(doc)
        else:
            directory = Path(self.config["directory"])
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    doc = self._process_file(file_path)
                    if doc:
                        documents.append(doc)
                        self.logger.debug(f"Processed file: {file_path}")

        return documents

    def get_document_updates(self, since: datetime) -> List[DocumentMetadata]:
        """
        Retrieve files modified since given timestamp
        """
        documents = []

        if "file_path" in self.config:
            path = Path(self.config["file_path"])
            if self._file_modified_after(path, since):
                doc = self._process_file(path)
                if doc:
                    documents.append(doc)
        else:
            directory = Path(self.config["directory"])
            for file_path in directory.rglob("*"):
                if file_path.is_file() and self._file_modified_after(file_path, since):
                    doc = self._process_file(file_path)
                    if doc:
                        documents.append(doc)

        return documents

    def _file_modified_after(self, file_path: Path, since: datetime) -> bool:
        """Check if file was modified after given timestamp"""
        try:
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            return mod_time > since
        except Exception:
            return False

    def _process_file(self, file_path: Path) -> Optional[DocumentMetadata]:
        """Process a single file"""
        try:
            # Skip unsupported file types
            if file_path.suffix.lower() not in self.processors:
                return None

            # Skip hidden files and temp files
            if file_path.name.startswith((".~", "~")):
                return None

            processor = self.processors[file_path.suffix.lower()]
            content = processor.extract_text(str(file_path))

            if not content:
                return None

            # Get file stats
            stat = file_path.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            create_time = datetime.fromtimestamp(stat.st_ctime)

            return DocumentMetadata(
                title=file_path.stem,
                content=content,
                source_type=file_path.suffix.lower()[1:],  # Remove leading dot
                source_url=f"file://{file_path.absolute()}",
                author=None,
                created_at=create_time,
                updated_at=mod_time,
                metadata={
                    "file_path": str(file_path),
                    "file_size": stat.st_size,
                    "file_type": file_path.suffix,
                },
            )
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {str(e)}")
            return None

    def connect(self):
        """No special connection needed for files"""
        if not self.test_connection():
            raise ConnectionError("File path not accessible")
        self.logger.info("File connector ready")

    def disconnect(self):
        """Cleanup"""
        self.logger.info("File connector disconnected")
