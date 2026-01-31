import requests
import json
from typing import Optional, List
from pathlib import Path

class GraphRAGClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def health_check(self) -> dict:
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def query(self, query: str) -> dict:
        payload = {"query": query}
        response = requests.post(
            f"{self.base_url}/query",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def ingest_file(self, file_path: str) -> dict:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/ingest",
                files=files
            )
        response.raise_for_status()
        return response.json()

    def ingest_files(self, file_paths: List[str]) -> dict:
        files = []
        for file_path in file_paths:
            with open(file_path, 'rb') as f:
                files.append(('files', f))

        response = requests.post(
            f"{self.base_url}/ingest-batch",
            files=files
        )
        response.raise_for_status()
        return response.json()

    def get_graph_stats(self) -> dict:
        response = requests.get(f"{self.base_url}/graph/stats")
        response.raise_for_status()
        return response.json()

    def get_entity(self, entity_id: str) -> dict:
        response = requests.get(
            f"{self.base_url}/graph/entity/{entity_id}"
        )
        response.raise_for_status()
        return response.json()

    def search_entities(self, query: str, entity_type: Optional[str] = None) -> dict:
        params = {"q": query}
        if entity_type:
            params["entity_type"] = entity_type

        response = requests.get(
            f"{self.base_url}/graph/search",
            params=params
        )
        response.raise_for_status()
        return response.json()

    def find_connections(self, entity1_id: str, entity2_id: str) -> dict:
        response = requests.post(
            f"{self.base_url}/graph/connections",
            params={
                "entity1_id": entity1_id,
                "entity2_id": entity2_id
            }
        )
        response.raise_for_status()
        return response.json()

    def reset_graph(self) -> dict:
        response = requests.delete(f"{self.base_url}/graph/reset")
        response.raise_for_status()
        return response.json()

    def interactive_query_loop(self):
        print("Graph RAG Query System (type 'exit' to quit)")
        print("-" * 50)

        while True:
            query = input("\nEnter your query: ").strip()
            if query.lower() == 'exit':
                break

            try:
                result = self.query(query)
                print("\nAnswer:")
                print(result["answer"])
                print("\nContext Used:")
                print(result["context_used"][:300] + "...")
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    client = GraphRAGClient()

    try:
        health = client.health_check()
        print(f"API Health: {health['status']}")
        print(f"Graph Stats: {health['graph_stats']}")
    except requests.exceptions.ConnectionError:
        print("Could not connect to API. Make sure it's running on http://localhost:8000")
        exit(1)

    client.interactive_query_loop()
