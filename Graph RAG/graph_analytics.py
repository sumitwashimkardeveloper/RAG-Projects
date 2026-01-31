from typing import List, Dict, Tuple
from graph_db import graph_db
import math

class GraphAnalytics:
    def __init__(self):
        self.db = graph_db

    def get_centrality_scores(self) -> List[Dict]:
        query = """
        MATCH (e:Entity)
        WITH e, size(()-[]->(e)) as in_degree, size((e)-[]-()) as out_degree
        WITH e, in_degree, out_degree, in_degree + out_degree as total_degree
        RETURN e.name as name, e.type as type, in_degree, out_degree, total_degree
        ORDER BY total_degree DESC
        LIMIT 20
        """
        return self.db.execute_query(query)

    def get_entity_clusters(self) -> List[Dict]:
        query = """
        MATCH (e:Entity)
        RETURN e.type as entity_type, count(*) as count
        ORDER BY count DESC
        """
        return self.db.execute_query(query)

    def find_entity_communities(self, start_entity: str, depth: int = 2) -> Dict:
        query = f"""
        MATCH (start:Entity {{name: '{start_entity}'}})
        MATCH path = (start)-[*1..{depth}]-(connected:Entity)
        RETURN connected.name as entity_name, connected.type as entity_type, length(path) as distance
        ORDER BY distance ASC
        """
        results = self.db.execute_query(query)
        return {
            "start_entity": start_entity,
            "community_members": results,
            "total_members": len(results)
        }

    def calculate_entity_similarity(self, entity1_name: str, entity2_name: str) -> float:
        query = f"""
        MATCH (e1:Entity {{name: '{entity1_name}'}})
        MATCH (e2:Entity {{name: '{entity2_name}'}})
        MATCH path = shortestPath((e1)-[*]-(e2))
        RETURN length(path) as distance
        """

        results = self.db.execute_query(query)
        if results and results[0].get('distance'):
            distance = results[0]['distance']
            similarity = 1.0 / (1.0 + distance)
            return round(similarity, 3)
        return 0.0

    def get_relationship_statistics(self) -> Dict:
        query = """
        MATCH ()-[r:RELATIONSHIP]->()
        WITH type(r) as rel_type
        RETURN rel_type, count(*) as count
        ORDER BY count DESC
        """
        rel_stats = self.db.execute_query(query)

        entity_query = """
        MATCH (e:Entity)
        RETURN e.type as entity_type, count(*) as count
        ORDER BY count DESC
        """
        entity_stats = self.db.execute_query(entity_query)

        return {
            "relationship_types": rel_stats,
            "entity_types": entity_stats
        }

    def find_bridging_entities(self, limit: int = 10) -> List[Dict]:
        query = f"""
        MATCH (e:Entity)-[r1:RELATIONSHIP]->(middle:Entity)-[r2:RELATIONSHIP]->(other:Entity)
        WHERE e <> other
        WITH middle, count(DISTINCT e) as source_connections, count(DISTINCT other) as target_connections
        RETURN middle.name as entity, middle.type as type, source_connections, target_connections, source_connections + target_connections as total_bridges
        ORDER BY total_bridges DESC
        LIMIT {limit}
        """
        return self.db.execute_query(query)

    def get_knowledge_gaps(self) -> Dict:
        query = """
        MATCH (e:Entity)
        WITH count(e) as total_entities
        MATCH (e:Entity)-[r]-()
        WITH total_entities, count(DISTINCT e) as connected_entities
        RETURN total_entities, connected_entities, total_entities - connected_entities as disconnected_entities,
               round(100.0 * connected_entities / total_entities, 2) as connectivity_percentage
        """
        results = self.db.execute_query(query)
        return results[0] if results else {}

    def recommend_connections(self, entity_name: str, limit: int = 5) -> Dict:
        entity_query = f"""
        MATCH (e:Entity {{name: '{entity_name}'}})
        RETURN e
        """
        entity_result = self.db.execute_query(entity_query)

        if not entity_result:
            return {"error": "Entity not found"}

        similar_type_query = f"""
        MATCH (e:Entity {{name: '{entity_name}'}})
        MATCH (other:Entity {{type: e.type}})
        WHERE other <> e AND NOT (e)--(other)
        RETURN other.name as recommended_entity, other.type as type, "same_type" as reason
        LIMIT {limit}
        """
        same_type = self.db.execute_query(similar_type_query)

        proximity_query = f"""
        MATCH (e:Entity {{name: '{entity_name}'}})
        MATCH (neighbor:Entity)--(e)
        MATCH (candidate:Entity)--(neighbor)
        WHERE candidate <> e AND NOT (candidate)--(e)
        WITH candidate, count(DISTINCT neighbor) as shared_neighbors
        RETURN candidate.name as recommended_entity, candidate.type as type, shared_neighbors, "through_proximity" as reason
        ORDER BY shared_neighbors DESC
        LIMIT {limit}
        """
        proximity = self.db.execute_query(proximity_query)

        return {
            "entity": entity_name,
            "same_type_recommendations": same_type,
            "proximity_recommendations": proximity
        }

    def export_subgraph(self, center_entity: str, radius: int = 2) -> Dict:
        query = f"""
        MATCH (center:Entity {{name: '{center_entity}'}})
        MATCH path = (center)-[*1..{radius}]-(node:Entity)
        UNWIND nodes(path) as node
        WITH collect(DISTINCT {{name: node.name, type: node.type}}) as entities
        MATCH (center)-[r*1..{radius}]-(end)
        RETURN {{
            center: center.name,
            entities: entities,
            radius: {radius}
        }}
        """
        results = self.db.execute_query(query)
        return results[0] if results else {}

    def detect_entity_duplicates(self) -> List[Dict]:
        query = """
        MATCH (e1:Entity), (e2:Entity)
        WHERE e1 <> e2 AND
              toLower(e1.name) = toLower(e2.name) AND
              e1.type = e2.type
        RETURN e1.name as entity_name, e1.type as type, count(*) as duplicate_count
        LIMIT 20
        """
        return self.db.execute_query(query)

graph_analytics = GraphAnalytics()
