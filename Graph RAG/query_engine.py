from typing import List, Dict, Optional
from entity_extractor import entity_extractor
from graph_db import graph_db
from config import settings

class GraphQueryEngine:
    def __init__(self):
        self.entity_extractor = entity_extractor

    def parse_query(self, query: str) -> Dict:
        entities, relations = self.entity_extractor.extract_entities_and_relations(query)

        return {
            "original_query": query,
            "entities": entities,
            "relations": relations
        }

    def search_entities(self, entity_name: str, entity_type: Optional[str] = None) -> List[Dict]:
        results = graph_db.search_entities(
            entity_name,
            entity_type,
            limit=settings.top_k_entities
        )
        return results

    def get_entity_context(self, entity_id: str, depth: int = 2) -> Dict:
        entity = graph_db.get_entity(entity_id)
        if not entity:
            return {"found": False}

        neighbors = graph_db.get_entity_neighbors(entity_id, depth)

        context_query = f"""
        MATCH (e:Entity {{id: "{entity_id}"}})
        MATCH (e)-[r]-(n:Entity)
        RETURN e, type(r) as relationship_type, n
        LIMIT 20
        """

        context = graph_db.execute_query(context_query)

        return {
            "found": True,
            "entity": entity,
            "relationships": context,
            "neighbor_count": len(neighbors)
        }

    def find_connections(self, entity1_id: str, entity2_id: str) -> Dict:
        paths = graph_db.find_paths(entity1_id, entity2_id, max_length=3)

        return {
            "entity1": entity1_id,
            "entity2": entity2_id,
            "path_count": len(paths),
            "paths": paths
        }

    def execute_graph_query(self, query_str: str) -> Dict:
        parsed = self.parse_query(query_str)

        entity_results = []
        for entity in parsed["entities"]:
            results = self.search_entities(
                entity.get("name"),
                entity.get("type")
            )
            entity_results.append({
                "query_entity": entity,
                "results": results
            })

        context_results = []
        for entity_result in entity_results:
            for result in entity_result["results"][:settings.top_k_entities]:
                entity_id = result.get("id")
                if entity_id:
                    context = self.get_entity_context(entity_id)
                    context_results.append(context)

        connection_results = []
        if len(entity_results) > 1 and len(entity_results[0]["results"]) > 0:
            if len(entity_results[1]["results"]) > 0:
                entity1_id = entity_results[0]["results"][0].get("id")
                entity2_id = entity_results[1]["results"][0].get("id")
                if entity1_id and entity2_id:
                    connections = self.find_connections(entity1_id, entity2_id)
                    connection_results.append(connections)

        return {
            "query": query_str,
            "parsed_entities": entity_results,
            "entity_context": context_results,
            "connections": connection_results
        }

    def get_graph_summary(self) -> Dict:
        stats = graph_db.get_graph_stats()

        top_entities_query = """
        MATCH (e:Entity)
        RETURN e.name as name, e.type as type, size(()-[]->(e)) as in_degree
        ORDER BY in_degree DESC
        LIMIT 10
        """

        top_entities = graph_db.execute_query(top_entities_query)

        relationship_types_query = """
        MATCH ()-[r]->()
        RETURN type(r) as relationship_type, count(*) as count
        ORDER BY count DESC
        """

        rel_types = graph_db.execute_query(relationship_types_query)

        return {
            "stats": stats,
            "top_entities": top_entities,
            "relationship_types": rel_types
        }

query_engine = GraphQueryEngine()
