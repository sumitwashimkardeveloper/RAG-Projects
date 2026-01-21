"""
Confluence Data Source Connector
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from atlassian import Confluence

from app.connectors.base import BaseConnector, DocumentMetadata

logger = logging.getLogger(__name__)


class ConfluenceConnector(BaseConnector):
    """
    Connector for Atlassian Confluence
    Extracts pages from specified spaces
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None

    def _validate_config(self):
        """Validate required Confluence configuration"""
        required = ["url", "username", "api_token"]
        missing = [k for k in required if k not in self.config]
        if missing:
            raise ValueError(f"Missing required config: {missing}")

    def test_connection(self) -> bool:
        """Test Confluence connection"""
        try:
            self.client = Confluence(
                url=self.config["url"],
                username=self.config["username"],
                password=self.config["api_token"],
            )
            self.client.get_all_spaces(limit=1)
            return True
        except Exception as e:
            self.logger.error(f"Confluence connection failed: {str(e)}")
            return False

    def connect(self):
        """Establish Confluence connection"""
        if not self.test_connection():
            raise ConnectionError("Failed to connect to Confluence")
        self.logger.info("Connected to Confluence")

    def get_documents(self) -> List[DocumentMetadata]:
        """
        Retrieve all documents from specified Confluence spaces
        """
        if not self.client:
            self.connect()

        documents = []
        spaces = self.config.get("spaces", [])

        for space_key in spaces:
            try:
                pages = self._get_space_pages(space_key)
                documents.extend(pages)
                self.logger.info(f"Retrieved {len(pages)} pages from space {space_key}")
            except Exception as e:
                self.logger.error(f"Error retrieving space {space_key}: {str(e)}")

        return documents

    def get_document_updates(self, since: datetime) -> List[DocumentMetadata]:
        """
        Retrieve pages updated since given timestamp
        """
        if not self.client:
            self.connect()

        documents = []
        spaces = self.config.get("spaces", [])
        since_str = since.isoformat()

        for space_key in spaces:
            try:
                cql = f'space = {space_key} AND updated >= "{since_str}"'
                pages = self.client.cql(cql, limit=1000)

                for page in pages.get("results", []):
                    doc = self._parse_page(page, space_key)
                    if doc:
                        documents.append(doc)

                self.logger.info(
                    f"Retrieved {len(pages.get('results', []))} updated pages from {space_key}"
                )
            except Exception as e:
                self.logger.error(f"Error retrieving updates from {space_key}: {str(e)}")

        return documents

    def _get_space_pages(self, space_key: str) -> List[DocumentMetadata]:
        """Get all pages from a specific space"""
        documents = []
        start = 0
        limit = 50

        while True:
            try:
                pages = self.client.get_all_pages_from_space(
                    space_key, start=start, limit=limit, expand="body.storage,metadata.labels"
                )

                if not pages:
                    break

                for page in pages:
                    doc = self._parse_page(page, space_key)
                    if doc:
                        documents.append(doc)

                start += limit
            except Exception as e:
                self.logger.error(f"Error fetching pages from {space_key}: {str(e)}")
                break

        return documents

    def _parse_page(self, page: Dict[str, Any], space_key: str) -> Optional[DocumentMetadata]:
        """Parse Confluence page to DocumentMetadata"""
        try:
            content = page.get("body", {}).get("storage", {}).get("value", "")

            # Extract plain text (remove HTML tags)
            import re
            text = re.sub(r"<[^>]+>", "", content)
            text = re.sub(r"\n+", "\n", text).strip()

            if not text:
                return None

            # Parse timestamps
            version = page.get("version", {})
            created_str = version.get("when", "")
            created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00")) if created_str else None

            # Get author
            author = page.get("version", {}).get("by", {}).get("displayName", "Unknown")

            return DocumentMetadata(
                title=page.get("title", "Untitled"),
                content=text,
                source_type="confluence",
                source_url=f"{self.config['url']}/wiki{page.get('_links', {}).get('webui', '')}",
                author=author,
                created_at=created_at,
                updated_at=created_at,
                metadata={
                    "space_key": space_key,
                    "page_id": page.get("id"),
                    "labels": [label.get("name") for label in page.get("metadata", {}).get("labels", [])],
                },
            )
        except Exception as e:
            self.logger.error(f"Error parsing Confluence page: {str(e)}")
            return None

    def disconnect(self):
        """Close Confluence connection"""
        self.client = None
        self.logger.info("Disconnected from Confluence")
