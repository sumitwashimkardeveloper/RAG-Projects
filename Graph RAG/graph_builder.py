from typing import List, Dict, Tuple
from entity_extractor import entity_extractor
from graph_db import graph_db
import hashlib

class GraphBuilder:
    def __init__(self):
        self.processed_chunks = set()

    def build_graph_from_chunks(self, chunks: List[str], doc_id: str) -> Dict:
        stats = {
            "total_chunks": len(chunks),
            "entities_extracted": 0,
            "relationships_extracted": 0,
            "errors": []
        }

        for idx, chunk in enumerate(chunks):
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()

            if chunk_hash in self.processed_chunks:
                continue

            self.processed_chunks.add(chunk_hash)

            try:
                entities, relationships = entity_extractor.extract_entities_and_relations(chunk)

                for entity in entities:
                    entity_id = f"{entity.get('id')}_{doc_id}_{idx}"
                    properties = {
                        "name": entity.get("name", ""),
                        "description": entity.get("description", ""),
                        "chunk_id": idx,
                        "doc_id": doc_id,
                        "source": f"doc_{doc_id}"
                    }

                    graph_db.create_entity(
                        entity_id,
                        entity.get("type", "CONCEPT"),
                        properties
                    )
                    stats["entities_extracted"] += 1

                for rel in relationships:
                    try:
                        source_id = f"{rel.get('source')}_{doc_id}_{idx}"
                        target_id = f"{rel.get('target')}_{doc_id}_{idx}"

                        rel_properties = {
                            "description": rel.get("description", ""),
                            "chunk_id": idx,
                            "doc_id": doc_id
                        }

                        graph_db.create_relationship(
                            source_id,
                            target_id,
                            rel.get("type", "RELATED_TO"),
                            rel_properties
                        )
                        stats["relationships_extracted"] += 1
                    except Exception as e:
                        stats["errors"].append(f"Relationship error in chunk {idx}: {str(e)}")

            except Exception as e:
                stats["errors"].append(f"Extraction error in chunk {idx}: {str(e)}")

        return stats

    def build_graph_from_documents(self, documents: List[Tuple[List[str], str]]) -> Dict:
        overall_stats = {
            "total_documents": len(documents),
            "total_chunks": 0,
            "total_entities": 0,
            "total_relationships": 0,
            "document_stats": []
        }

        for chunks, doc_id in documents:
            stats = self.build_graph_from_chunks(chunks, doc_id)
            overall_stats["total_chunks"] += stats["total_chunks"]
            overall_stats["total_entities"] += stats["entities_extracted"]
            overall_stats["total_relationships"] += stats["relationships_extracted"]
            overall_stats["document_stats"].append({
                "doc_id": doc_id,
                "stats": stats
            })

        return overall_stats

    def consolidate_entities(self) -> Dict:
        result = graph_db.execute_query("""
        MATCH (e:Entity)
        RETURN e.name as name, e.type as type, count(*) as count
        ORDER BY count DESC
        """)

        stats = {
            "total_unique_entities": len(result),
            "entity_summary": result
        }

        return stats

graph_builder = GraphBuilder()
