from typing import List, Dict

class CypherQueryBuilder:
    @staticmethod
    def find_all_entities() -> str:
        return "MATCH (e:Entity) RETURN e"

    @staticmethod
    def find_entities_by_type(entity_type: str) -> str:
        return f"MATCH (e:Entity {{type: '{entity_type}'}}) RETURN e"

    @staticmethod
    def find_entity_by_name(name: str) -> str:
        return f"MATCH (e:Entity {{name: '{name}'}}) RETURN e"

    @staticmethod
    def find_entities_by_pattern(pattern: str) -> str:
        return f"MATCH (e:Entity) WHERE e.name CONTAINS '{pattern}' RETURN e"

    @staticmethod
    def get_entity_neighbors(entity_id: str, depth: int = 1) -> str:
        return f"""
        MATCH (e:Entity {{id: '{entity_id}'}})
        MATCH (e)-[r*1..{depth}]-(neighbor:Entity)
        RETURN neighbor, relationship
        """

    @staticmethod
    def find_shortest_path(source: str, target: str) -> str:
        return f"""
        MATCH (s:Entity {{id: '{source}'}}), (t:Entity {{id: '{target}'}})
        MATCH path = shortestPath((s)-[*]-(t))
        RETURN path, length(path) as distance
        """

    @staticmethod
    def find_all_paths(source: str, target: str, max_length: int = 3) -> str:
        return f"""
        MATCH (s:Entity {{id: '{source}'}}), (t:Entity {{id: '{target}'}})
        MATCH path = (s)-[*1..{max_length}]-(t)
        RETURN path, length(path) as distance
        ORDER BY distance
        LIMIT 10
        """

    @staticmethod
    def get_relationship_between(entity1: str, entity2: str) -> str:
        return f"""
        MATCH (e1:Entity {{id: '{entity1}'}})
        MATCH (e2:Entity {{id: '{entity2}'}})
        MATCH (e1)-[r]-(e2)
        RETURN type(r) as relationship_type, r
        """

    @staticmethod
    def find_common_neighbors(entity1: str, entity2: str) -> str:
        return f"""
        MATCH (e1:Entity {{id: '{entity1}'}})--(common:Entity)--(e2:Entity {{id: '{entity2}'}})
        RETURN DISTINCT common
        """

    @staticmethod
    def get_entity_stats() -> str:
        return """
        MATCH (e:Entity)
        RETURN
            count(e) as total_entities,
            count(DISTINCT e.type) as unique_types,
            size(()-[]->(e)) as avg_in_degree,
            size((e)-[]-()) as avg_out_degree
        """

    @staticmethod
    def get_relationships_stats() -> str:
        return """
        MATCH ()-[r:RELATIONSHIP]->()
        RETURN
            count(r) as total_relationships,
            count(DISTINCT type(r)) as unique_types,
            type(r) as relationship_type
        ORDER BY count(r) DESC
        """

    @staticmethod
    def find_isolated_entities() -> str:
        return """
        MATCH (e:Entity)
        WHERE size(()-[]->(e)) = 0 AND size((e)-[]-()) = 0
        RETURN e
        """

    @staticmethod
    def find_hubs(min_degree: int = 5) -> str:
        return f"""
        MATCH (e:Entity)
        WITH e, size(()-[]->(e)) + size((e)-[]-()) as degree
        WHERE degree > {min_degree}
        RETURN e.name, e.type, degree
        ORDER BY degree DESC
        """

    @staticmethod
    def traverse_graph_by_type(start_entity: str, entity_type: str, depth: int = 2) -> str:
        return f"""
        MATCH (start:Entity {{id: '{start_entity}'}})
        MATCH (start)-[*1..{depth}]-(target:Entity {{type: '{entity_type}'}})
        RETURN DISTINCT target
        """

    @staticmethod
    def find_entity_chains(start_type: str, end_type: str, depth: int = 3) -> str:
        return f"""
        MATCH (start:Entity {{type: '{start_type}'}})
        MATCH (end:Entity {{type: '{end_type}'}})
        MATCH path = shortestPath((start)-[*1..{depth}]-(end))
        RETURN path, length(path) as chain_length
        ORDER BY chain_length
        LIMIT 5
        """

    @staticmethod
    def merge_duplicate_entities(original_id: str, duplicate_id: str) -> str:
        return f"""
        MATCH (orig:Entity {{id: '{original_id}'}}), (dup:Entity {{id: '{duplicate_id}'}})
        MATCH (dup)-[r]->(other)
        CREATE (orig)-[new_r:RELATIONSHIP]->(other)
        SET new_r += r
        DELETE r, dup
        RETURN orig
        """

    @staticmethod
    def get_entity_metadata(entity_id: str) -> str:
        return f"""
        MATCH (e:Entity {{id: '{entity_id}'}})
        RETURN e, keys(e) as properties
        """

    @staticmethod
    def find_entities_by_source(source: str) -> str:
        return f"""
        MATCH (e:Entity {{source: '{source}'}})
        RETURN e
        """

    @staticmethod
    def update_entity_property(entity_id: str, property_key: str, property_value: str) -> str:
        return f"""
        MATCH (e:Entity {{id: '{entity_id}'}})
        SET e.{property_key} = '{property_value}'
        RETURN e
        """

    @staticmethod
    def bulk_delete_by_source(source: str) -> str:
        return f"""
        MATCH (e:Entity {{source: '{source}'}})
        DETACH DELETE e
        """

    @staticmethod
    def calculate_entity_similarity_cosine(entity1: str, entity2: str) -> str:
        return f"""
        MATCH (e1:Entity {{id: '{entity1}'}})
        MATCH (e2:Entity {{id: '{entity2}'}})
        MATCH (e1)-[r1]-(shared:Entity)-[r2]-(e2)
        WITH count(DISTINCT shared) as shared_neighbors
        MATCH (e1)-[r1]-(neighbor1:Entity)
        WITH shared_neighbors, count(DISTINCT neighbor1) as neighbors_e1
        MATCH (e2)-[r2]-(neighbor2:Entity)
        WITH shared_neighbors, neighbors_e1, count(DISTINCT neighbor2) as neighbors_e2
        RETURN
            CASE WHEN neighbors_e1 * neighbors_e2 = 0 THEN 0
            ELSE round(toFloat(shared_neighbors * 100) / sqrt(neighbors_e1 * neighbors_e2), 2)
            END as cosine_similarity
        """

cypher_builder = CypherQueryBuilder()
