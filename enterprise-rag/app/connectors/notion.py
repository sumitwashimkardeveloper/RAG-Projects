"""
Notion Data Source Connector
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from notion_client import Client

from app.connectors.base import BaseConnector, DocumentMetadata

logger = logging.getLogger(__name__)


class NotionConnector(BaseConnector):
    """
    Connector for Notion
    Extracts pages and database content
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None

    def _validate_config(self):
        """Validate required Notion configuration"""
        if "api_key" not in self.config:
            raise ValueError("Missing required config: api_key")

    def test_connection(self) -> bool:
        """Test Notion connection"""
        try:
            self.client = Client(auth=self.config["api_key"])
            self.client.users.list()
            return True
        except Exception as e:
            self.logger.error(f"Notion connection failed: {str(e)}")
            return False

    def connect(self):
        """Establish Notion connection"""
        if not self.test_connection():
            raise ConnectionError("Failed to connect to Notion")
        self.logger.info("Connected to Notion")

    def get_documents(self) -> List[DocumentMetadata]:
        """
        Retrieve all documents from specified Notion databases/pages
        """
        if not self.client:
            self.connect()

        documents = []
        database_ids = self.config.get("database_ids", [])

        for db_id in database_ids:
            try:
                results = self._query_database(db_id)
                documents.extend(results)
                self.logger.info(f"Retrieved {len(results)} items from database {db_id}")
            except Exception as e:
                self.logger.error(f"Error querying database {db_id}: {str(e)}")

        return documents

    def get_document_updates(self, since: datetime) -> List[DocumentMetadata]:
        """
        Retrieve items updated since given timestamp
        """
        if not self.client:
            self.connect()

        documents = []
        database_ids = self.config.get("database_ids", [])

        for db_id in database_ids:
            try:
                results = self._query_database(
                    db_id,
                    filter_dict={
                        "property": "Last edited time",
                        "date": {"after": since.isoformat()},
                    },
                )
                documents.extend(results)
            except Exception as e:
                self.logger.error(f"Error querying database {db_id}: {str(e)}")

        return documents

    def _query_database(self, database_id: str, filter_dict: Optional[Dict] = None) -> List[DocumentMetadata]:
        """Query a Notion database and extract documents"""
        documents = []
        has_more = True
        cursor = None

        while has_more:
            try:
                kwargs = {"database_id": database_id}
                if filter_dict:
                    kwargs["filter"] = filter_dict
                if cursor:
                    kwargs["start_cursor"] = cursor

                response = self.client.databases.query(**kwargs)

                for item in response.get("results", []):
                    doc = self._parse_page(item)
                    if doc:
                        documents.append(doc)

                has_more = response.get("has_more", False)
                cursor = response.get("next_cursor")
            except Exception as e:
                self.logger.error(f"Error querying database: {str(e)}")
                break

        return documents

    def _parse_page(self, page: Dict[str, Any]) -> Optional[DocumentMetadata]:
        """Parse Notion page to DocumentMetadata"""
        try:
            # Extract title
            title = self._extract_title(page)
            if not title:
                return None

            # Extract content from blocks
            content = self._extract_page_content(page["id"])
            if not content:
                return None

            # Parse timestamps
            created_at = datetime.fromisoformat(page.get("created_time", "").replace("Z", "+00:00"))
            updated_at = datetime.fromisoformat(page.get("last_edited_time", "").replace("Z", "+00:00"))

            return DocumentMetadata(
                title=title,
                content=content,
                source_type="notion",
                source_url=page.get("url", ""),
                created_at=created_at,
                updated_at=updated_at,
                metadata={
                    "notion_id": page.get("id"),
                    "properties": page.get("properties", {}),
                },
            )
        except Exception as e:
            self.logger.error(f"Error parsing Notion page: {str(e)}")
            return None

    def _extract_title(self, page: Dict[str, Any]) -> Optional[str]:
        """Extract title from Notion page"""
        try:
            properties = page.get("properties", {})

            # Look for common title properties
            for prop_name, prop_value in properties.items():
                if prop_value.get("type") == "title":
                    title_array = prop_value.get("title", [])
                    return "".join([t.get("plain_text", "") for t in title_array]) or None

            return None
        except Exception:
            return None

    def _extract_page_content(self, page_id: str) -> Optional[str]:
        """Extract content from Notion page blocks"""
        try:
            content_parts = []
            cursor = None
            has_more = True

            while has_more:
                kwargs = {"block_id": page_id}
                if cursor:
                    kwargs["start_cursor"] = cursor

                response = self.client.blocks.children.list(**kwargs)

                for block in response.get("results", []):
                    text = self._extract_block_text(block)
                    if text:
                        content_parts.append(text)

                has_more = response.get("has_more", False)
                cursor = response.get("next_cursor")

            return "\n".join(content_parts) if content_parts else None
        except Exception as e:
            self.logger.error(f"Error extracting page content: {str(e)}")
            return None

    def _extract_block_text(self, block: Dict[str, Any]) -> Optional[str]:
        """Extract text from a Notion block"""
        try:
            block_type = block.get("type")
            block_data = block.get(block_type, {})

            # Extract text from rich text fields
            if "rich_text" in block_data:
                text_parts = []
                for text_obj in block_data["rich_text"]:
                    if text_obj.get("type") == "text":
                        text_parts.append(text_obj.get("text", {}).get("content", ""))
                return "".join(text_parts) if text_parts else None

            # Handle heading blocks
            if block_type in ["heading_1", "heading_2", "heading_3", "paragraph"]:
                text_parts = []
                for text_obj in block_data.get("rich_text", []):
                    text_parts.append(text_obj.get("text", {}).get("content", ""))
                return "".join(text_parts) if text_parts else None

            return None
        except Exception:
            return None

    def disconnect(self):
        """Close Notion connection"""
        self.client = None
        self.logger.info("Disconnected from Notion")
