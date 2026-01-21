"""
Base Connector Class for Data Source Connectors
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Standard metadata for ingested documents"""
    title: str
    content: str
    source_type: str
    source_url: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseConnector(ABC):
    """
    Abstract base class for all data source connectors
    Defines interface for connecting to external data sources
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize connector with configuration

        Args:
            config: Dictionary with source-specific configuration
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._validate_config()

    @abstractmethod
    def _validate_config(self):
        """Validate that required config parameters are present"""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if connection to data source is successful

        Returns:
            True if connection succeeds, False otherwise
        """
        pass

    @abstractmethod
    def get_documents(self) -> List[DocumentMetadata]:
        """
        Retrieve all documents from the data source

        Returns:
            List of DocumentMetadata objects
        """
        pass

    @abstractmethod
    def get_document_updates(self, since: datetime) -> List[DocumentMetadata]:
        """
        Retrieve documents updated since given timestamp
        Used for incremental sync

        Args:
            since: Datetime to retrieve updates from

        Returns:
            List of updated DocumentMetadata objects
        """
        pass

    def connect(self):
        """
        Establish connection to data source
        Called before operations
        """
        if not self.test_connection():
            raise ConnectionError(f"Failed to connect to {self.__class__.__name__}")
        self.logger.info(f"Connected to {self.__class__.__name__}")

    def disconnect(self):
        """
        Close connection to data source
        Override if cleanup is needed
        """
        pass

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
