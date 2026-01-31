from graph_db import graph_db

def init_neo4j_schema():
    queries = [
        "CREATE INDEX idx_entity_id IF NOT EXISTS FOR (e:Entity) ON (e.id)",
        "CREATE INDEX idx_entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
        "CREATE INDEX idx_entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)",
        "CREATE INDEX idx_doc_id IF NOT EXISTS FOR (e:Entity) ON (e.doc_id)",
        "CREATE CONSTRAINT unique_entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
    ]

    for query in queries:
        try:
            graph_db.execute_query(query)
            print(f"✓ Executed: {query[:50]}...")
        except Exception as e:
            print(f"✗ Failed: {query[:50]}... - {str(e)}")

    print("\nSchema initialization completed!")

def get_entity_type_distribution():
    query = """
    MATCH (e:Entity)
    RETURN e.type as type, count(*) as count
    ORDER BY count DESC
    """
    return graph_db.execute_query(query)

def get_relationship_type_distribution():
    query = """
    MATCH ()-[r:RELATIONSHIP]->()
    RETURN r.type as type, count(*) as count
    ORDER BY count DESC
    """
    return graph_db.execute_query(query)

def get_most_connected_entities(limit: int = 10):
    query = f"""
    MATCH (e:Entity)
    WITH e, size(()-[]->(e)) as in_degree, size((e)-[]-()) as out_degree
    RETURN e.name as name, e.type as type, in_degree + out_degree as total_connections
    ORDER BY total_connections DESC
    LIMIT {limit}
    """
    return graph_db.execute_query(query)

def cleanup_orphaned_entities():
    query = """
    MATCH (e:Entity)
    WHERE size(()-[]->(e)) = 0 AND size((e)-[]-()) = 0
    RETURN count(e) as orphaned_count
    """
    result = graph_db.execute_query(query)
    orphaned_count = result[0]['orphaned_count'] if result else 0

    if orphaned_count > 0:
        delete_query = """
        MATCH (e:Entity)
        WHERE size(()-[]->(e)) = 0 AND size((e)-[]-()) = 0
        DELETE e
        """
        graph_db.execute_query(delete_query)
        print(f"Removed {orphaned_count} orphaned entities")

    return orphaned_count

def export_graph_statistics():
    stats = {}

    entity_dist = get_entity_type_distribution()
    stats['entity_type_distribution'] = entity_dist

    rel_dist = get_relationship_type_distribution()
    stats['relationship_type_distribution'] = rel_dist

    top_entities = get_most_connected_entities(10)
    stats['top_connected_entities'] = top_entities

    total_stats = graph_db.get_graph_stats()
    stats['total_stats'] = total_stats

    return stats

if __name__ == "__main__":
    import json

    print("Initializing Neo4j Schema...")
    init_neo4j_schema()

    print("\nGetting graph statistics...")
    stats = export_graph_statistics()

    print("\nGraph Statistics:")
    print(json.dumps(stats, indent=2, default=str))

    print("\nTop Connected Entities:")
    for entity in get_most_connected_entities(5):
        print(f"  - {entity['name']}: {entity['total_connections']} connections")
