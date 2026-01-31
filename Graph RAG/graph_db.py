from neo4j import GraphDatabase, Session
from typing import Dict, List, Any, Optional
from config import settings

class GraphDatabase:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )

    def close(self):
        self.driver.close()

    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    def create_entity(self, entity_id: str, entity_type: str, properties: Dict) -> bool:
        query = """
        MERGE (e:Entity {id: $entity_id})
        SET e.type = $entity_type, e += $properties
        RETURN e
        """
        with self.driver.session() as session:
            session.run(query, {
                "entity_id": entity_id,
                "entity_type": entity_type,
                "properties": properties
            })
        return True

    def create_relationship(self, source_id: str, target_id: str,
                          rel_type: str, properties: Dict) -> bool:
        query = """
        MATCH (s:Entity {id: $source_id})
        MATCH (t:Entity {id: $target_id})
        CREATE (s)-[r:RELATIONSHIP {type: $rel_type}]->(t)
        SET r += $properties
        RETURN r
        """
        with self.driver.session() as session:
            session.run(query, {
                "source_id": source_id,
                "target_id": target_id,
                "rel_type": rel_type,
                "properties": properties
            })
        return True

    def get_entity(self, entity_id: str) -> Optional[Dict]:
        query = """
        MATCH (e:Entity {id: $entity_id})
        RETURN e
        """
        with self.driver.session() as session:
            result = session.run(query, {"entity_id": entity_id})
            record = result.single()
            return record["e"] if record else None

    def get_entity_neighbors(self, entity_id: str, depth: int = 1) -> List[Dict]:
        query = """
        MATCH (e:Entity {id: $entity_id})
        CALL apoc.path.expandConfig(e, {
            relationshipFilter: ">",
            maxLevel: $depth
        })
        YIELD path
        RETURN path
        """
        with self.driver.session() as session:
            result = session.run(query, {
                "entity_id": entity_id,
                "depth": depth
            })
            return [{"path": record["path"]} for record in result]

    def find_paths(self, source_id: str, target_id: str,
                   max_length: int = 3) -> List[Dict]:
        query = """
        MATCH (s:Entity {id: $source_id}), (t:Entity {id: $target_id})
        MATCH path = shortestPath((s)-[*...$max_length]-(t))
        RETURN path, length(path) as path_length
        ORDER BY path_length
        """
        with self.driver.session() as session:
            result = session.run(query, {
                "source_id": source_id,
                "target_id": target_id,
                "max_length": max_length
            })
            return [{"path": record["path"], "length": record["path_length"]}
                   for record in result]

    def search_entities(self, query_text: str, entity_type: str = None,
                       limit: int = 10) -> List[Dict]:
        if entity_type:
            cypher = """
            MATCH (e:Entity {type: $entity_type})
            WHERE e.name CONTAINS $query_text OR e.description CONTAINS $query_text
            RETURN e
            LIMIT $limit
            """
            params = {
                "query_text": query_text,
                "entity_type": entity_type,
                "limit": limit
            }
        else:
            cypher = """
            MATCH (e:Entity)
            WHERE e.name CONTAINS $query_text OR e.description CONTAINS $query_text
            RETURN e
            LIMIT $limit
            """
            params = {
                "query_text": query_text,
                "limit": limit
            }

        with self.driver.session() as session:
            result = session.run(cypher, params)
            return [record["e"] for record in result]

    def delete_all(self) -> bool:
        query = "MATCH (n) DETACH DELETE n"
        with self.driver.session() as session:
            session.run(query)
        return True

    def get_graph_stats(self) -> Dict:
        query = """
        MATCH (e:Entity)
        WITH count(e) as entity_count
        MATCH ()-[r]-()
        WITH entity_count, count(r) as relationship_count
        RETURN entity_count, relationship_count
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            return {
                "entities": record["entity_count"],
                "relationships": record["relationship_count"]
            } if record else {"entities": 0, "relationships": 0}

graph_db = GraphDatabase()
